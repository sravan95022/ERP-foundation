from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.inventory import Warehouse, Stock, StockMovement
from app.schemas.inventory import (
    WarehouseCreate, WarehouseOut, StockAdjust, StockOut,
    StockMovementOut, ReconciliationResult,
)
from app.services import inventory_service

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory & Warehouse"])


@router.post("/warehouses", response_model=WarehouseOut, status_code=201)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    wh = Warehouse(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(wh); db.commit(); db.refresh(wh)
    return wh


@router.get("/warehouses", response_model=List[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Warehouse).filter(Warehouse.tenant_id == user.tenant_id).all()


@router.post("/stock/adjust", response_model=StockOut)
def adjust_stock(payload: StockAdjust, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return inventory_service.adjust_stock(db, user.tenant_id, payload)


@router.get("/stock", response_model=List[StockOut])
def list_stock(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Stock).filter(Stock.tenant_id == user.tenant_id).all()


@router.get("/movements", response_model=List[StockMovementOut])
def list_movements(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(StockMovement)
        .filter(StockMovement.tenant_id == user.tenant_id)
        .order_by(StockMovement.created_at.desc())
        .all()
    )


@router.get("/reconcile", response_model=ReconciliationResult)
def reconcile_stock(
    product_id: int, warehouse_id: int,
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    return inventory_service.reconcile(db, user.tenant_id, product_id, warehouse_id)
