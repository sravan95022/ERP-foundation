from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.sales import SalesOrder, Invoice
from app.schemas.sales import SalesOrderCreate, SalesOrderOut, InvoiceOut
from app.services import sales_service

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])


@router.post("/orders", response_model=SalesOrderOut, status_code=201)
def create_order(payload: SalesOrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order_number = f"SO-{payload.customer_id}-{int(payload.unit_price)}-{payload.product_id}"
    order = SalesOrder(tenant_id=user.tenant_id, order_number=order_number, **payload.model_dump())
    db.add(order); db.commit(); db.refresh(order)
    return order


@router.get("/orders", response_model=List[SalesOrderOut])
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(SalesOrder).filter(SalesOrder.tenant_id == user.tenant_id).all()


@router.post("/orders/{order_id}/confirm", response_model=SalesOrderOut)
def confirm_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return sales_service.confirm_order(db, user.tenant_id, order_id)


@router.post("/orders/{order_id}/invoice", response_model=InvoiceOut)
def invoice_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return sales_service.generate_invoice(db, user.tenant_id, order_id)


@router.get("/invoices", response_model=List[InvoiceOut])
def list_invoices(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Invoice).filter(Invoice.tenant_id == user.tenant_id).all()
