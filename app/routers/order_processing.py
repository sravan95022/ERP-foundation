from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.order_processing import Shipment, ReturnRequest, Refund, OrderStatusHistory, ShipmentStatus
from app.schemas.order_processing import ShipmentCreate, ShipmentOut, ReturnCreate, ReturnOut, RefundCreate, RefundOut

router = APIRouter(prefix="/api/v1/orders", tags=["Order Processing"])


@router.post("/shipments", response_model=ShipmentOut, status_code=201)
def create_shipment(payload: ShipmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    shipment = Shipment(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(shipment)
    db.add(OrderStatusHistory(tenant_id=user.tenant_id, sales_order_id=payload.sales_order_id, status="shipment_planned"))
    db.commit(); db.refresh(shipment)
    return shipment


@router.post("/shipments/{shipment_id}/mark-shipped", response_model=ShipmentOut)
def mark_shipped(shipment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id, Shipment.tenant_id == user.tenant_id).first()
    shipment.status = ShipmentStatus.SHIPPED
    db.add(OrderStatusHistory(tenant_id=user.tenant_id, sales_order_id=shipment.sales_order_id, status="shipped"))
    db.commit(); db.refresh(shipment)
    return shipment


@router.get("/status-history/{sales_order_id}")
def status_history(sales_order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(OrderStatusHistory).filter(
        OrderStatusHistory.sales_order_id == sales_order_id, OrderStatusHistory.tenant_id == user.tenant_id
    ).order_by(OrderStatusHistory.changed_at).all()
    return [{"status": r.status, "changed_at": r.changed_at} for r in rows]


@router.post("/returns", response_model=ReturnOut, status_code=201)
def create_return(payload: ReturnCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ret = ReturnRequest(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(ret); db.commit(); db.refresh(ret)
    return ret


@router.post("/refunds", response_model=RefundOut, status_code=201)
def create_refund(payload: RefundCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    refund = Refund(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(refund); db.commit(); db.refresh(refund)
    return refund
