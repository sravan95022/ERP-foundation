from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sales import SalesOrder, Invoice, SOStatus
from app.models.inventory import MovementType
from app.schemas.inventory import StockAdjust
from app.services import inventory_service, finance_service


def confirm_order(db: Session, tenant_id: int, order_id: int) -> SalesOrder:
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id, SalesOrder.tenant_id == tenant_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    if order.status != SOStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft orders can be confirmed")

    # Dispatch stock now — will raise if insufficient (Phase 16 guard)
    inventory_service.adjust_stock(db, tenant_id, StockAdjust(
        product_id=order.product_id, warehouse_id=order.warehouse_id,
        quantity=-order.quantity, movement_type=MovementType.DISPATCH, reference=order.order_number,
    ))

    order.status = SOStatus.CONFIRMED
    db.commit(); db.refresh(order)
    return order


def generate_invoice(db: Session, tenant_id: int, order_id: int) -> Invoice:
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id, SalesOrder.tenant_id == tenant_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    if order.status != SOStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Order must be confirmed before invoicing")

    subtotal = order.quantity * order.unit_price
    discount_amount = subtotal * (order.discount_percent / Decimal(100))
    taxable = subtotal - discount_amount
    tax_amount = taxable * (order.tax_percent / Decimal(100))
    total = taxable + tax_amount

    invoice_number = f"INV-{order.id}"
    invoice = Invoice(
        tenant_id=tenant_id, invoice_number=invoice_number, sales_order_id=order.id,
        customer_id=order.customer_id, subtotal=subtotal, discount_amount=discount_amount,
        tax_amount=tax_amount, total_amount=total,
    )
    db.add(invoice)
    order.status = SOStatus.INVOICED
    db.commit(); db.refresh(invoice)

    # Phase 20 integration: Dr Accounts Receivable, Cr Sales Revenue
    finance_service.post_journal_entry(
        db, tenant_id, reference=invoice_number, description="Sales invoice",
        lines=[
            {"account_code": "1100", "debit": float(total), "credit": 0},
            {"account_code": "4000", "debit": 0, "credit": float(total)},
        ],
    )
    return invoice
