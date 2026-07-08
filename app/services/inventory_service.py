from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.inventory import Stock, StockMovement, MovementType
from app.schemas.inventory import StockAdjust


def adjust_stock(db: Session, tenant_id: int, payload: StockAdjust) -> Stock:
    """Applies a stock movement and updates the current-quantity Stock row.
    Rejects any movement that would push quantity negative (Phase 15/16 rule)."""
    stock = (
        db.query(Stock)
        .filter(
            Stock.tenant_id == tenant_id,
            Stock.product_id == payload.product_id,
            Stock.warehouse_id == payload.warehouse_id,
        )
        .first()
    )

    if not stock:
        stock = Stock(
            tenant_id=tenant_id,
            product_id=payload.product_id,
            warehouse_id=payload.warehouse_id,
            quantity=Decimal("0"),
            batch_number=payload.batch_number,
        )
        db.add(stock)
        db.flush()

    new_quantity = stock.quantity + payload.quantity
    if new_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock: current={stock.quantity}, requested change={payload.quantity}",
        )

    stock.quantity = new_quantity
    if payload.batch_number:
        stock.batch_number = payload.batch_number

    movement = StockMovement(
        tenant_id=tenant_id,
        product_id=payload.product_id,
        warehouse_id=payload.warehouse_id,
        movement_type=payload.movement_type,
        quantity=payload.quantity,
        reference=payload.reference,
        batch_number=payload.batch_number,
    )
    db.add(movement)
    db.commit()
    db.refresh(stock)
    return stock


def reconcile(db: Session, tenant_id: int, product_id: int, warehouse_id: int) -> dict:
    """Compares the live Stock quantity against the sum of all StockMovements —
    the core of Phase 16's 'inventory reconciliation' requirement."""
    stock = (
        db.query(Stock)
        .filter(Stock.tenant_id == tenant_id, Stock.product_id == product_id, Stock.warehouse_id == warehouse_id)
        .first()
    )
    stock_qty = stock.quantity if stock else Decimal("0")

    movements_sum = (
        db.query(func.coalesce(func.sum(StockMovement.quantity), 0))
        .filter(
            StockMovement.tenant_id == tenant_id,
            StockMovement.product_id == product_id,
            StockMovement.warehouse_id == warehouse_id,
        )
        .scalar()
    )
    movements_sum = Decimal(str(movements_sum))

    return {
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "stock_table_quantity": stock_qty,
        "movements_sum": movements_sum,
        "is_balanced": stock_qty == movements_sum,
    }
