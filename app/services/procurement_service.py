from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.procurement import PurchaseRequest, PurchaseOrder, GoodsReceipt, VendorPayment, PRStatus, POStatus
from app.models.inventory import MovementType
from app.schemas.inventory import StockAdjust
from app.services import inventory_service, finance_service


def approve_pr(db: Session, tenant_id: int, pr_id: int) -> PurchaseRequest:
    pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id, PurchaseRequest.tenant_id == tenant_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    pr.status = PRStatus.APPROVED
    db.commit(); db.refresh(pr)
    return pr


def convert_pr_to_po(db: Session, tenant_id: int, pr_id: int, vendor_id: int, warehouse_id: int, unit_price: Decimal) -> PurchaseOrder:
    pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id, PurchaseRequest.tenant_id == tenant_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    if pr.status != PRStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Only approved requests can be converted to a PO")

    po_number = f"PO-{pr_id}-{int(unit_price)}"
    po = PurchaseOrder(
        tenant_id=tenant_id, po_number=po_number, vendor_id=vendor_id,
        product_id=pr.product_id, warehouse_id=warehouse_id,
        quantity_ordered=pr.quantity, unit_price=unit_price,
    )
    db.add(po)
    pr.status = PRStatus.CONVERTED
    db.commit(); db.refresh(po)
    return po


def receive_goods(db: Session, tenant_id: int, po_id: int, quantity: Decimal) -> GoodsReceipt:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    remaining = po.quantity_ordered - po.quantity_received
    if quantity > remaining:
        raise HTTPException(status_code=400, detail=f"Cannot receive more than remaining quantity ({remaining})")

    # Updates real stock via the inventory service (Phase 16 integration)
    inventory_service.adjust_stock(db, tenant_id, StockAdjust(
        product_id=po.product_id, warehouse_id=po.warehouse_id,
        quantity=quantity, movement_type=MovementType.RECEIPT, reference=po.po_number,
    ))

    receipt = GoodsReceipt(tenant_id=tenant_id, purchase_order_id=po.id, quantity_received=quantity)
    db.add(receipt)

    po.quantity_received += quantity
    po.status = POStatus.RECEIVED if po.quantity_received >= po.quantity_ordered else POStatus.PARTIALLY_RECEIVED
    db.commit(); db.refresh(receipt)
    return receipt


def pay_vendor(db: Session, tenant_id: int, po_id: int, amount: Decimal) -> VendorPayment:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    payment = VendorPayment(tenant_id=tenant_id, purchase_order_id=po_id, vendor_id=po.vendor_id, amount=amount)
    db.add(payment)
    db.commit(); db.refresh(payment)

    # Phase 20 integration: Dr Accounts Payable, Cr Cash
    finance_service.post_journal_entry(
        db, tenant_id, reference=f"Payment for {po.po_number}", description="Vendor payment",
        lines=[
            {"account_code": "2000", "debit": float(amount), "credit": 0},
            {"account_code": "1000", "debit": 0, "credit": float(amount)},
        ],
    )
    return payment
