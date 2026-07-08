from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.procurement import PurchaseRequest, PurchaseOrder
from app.schemas.procurement import (
    PRCreate, PROut, POConvert, POOut, GoodsReceiptCreate, GoodsReceiptOut,
    VendorPaymentCreate, VendorPaymentOut,
)
from app.services import procurement_service

router = APIRouter(prefix="/api/v1/procurement", tags=["Procurement"])


@router.post("/requests", response_model=PROut, status_code=201)
def create_pr(payload: PRCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pr = PurchaseRequest(tenant_id=user.tenant_id, requested_by=user.id, **payload.model_dump())
    db.add(pr); db.commit(); db.refresh(pr)
    return pr


@router.get("/requests", response_model=List[PROut])
def list_prs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(PurchaseRequest).filter(PurchaseRequest.tenant_id == user.tenant_id).all()


@router.post("/requests/{pr_id}/approve", response_model=PROut)
def approve_pr(pr_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return procurement_service.approve_pr(db, user.tenant_id, pr_id)


@router.post("/requests/{pr_id}/convert-to-po", response_model=POOut)
def convert_to_po(pr_id: int, payload: POConvert, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return procurement_service.convert_pr_to_po(db, user.tenant_id, pr_id, payload.vendor_id, payload.warehouse_id, payload.unit_price)


@router.get("/orders", response_model=List[POOut])
def list_pos(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(PurchaseOrder).filter(PurchaseOrder.tenant_id == user.tenant_id).all()


@router.post("/goods-receipt", response_model=GoodsReceiptOut, status_code=201)
def receive_goods(payload: GoodsReceiptCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return procurement_service.receive_goods(db, user.tenant_id, payload.purchase_order_id, payload.quantity)


@router.post("/vendor-payments", response_model=VendorPaymentOut, status_code=201)
def pay_vendor(payload: VendorPaymentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return procurement_service.pay_vendor(db, user.tenant_id, payload.purchase_order_id, payload.amount)
