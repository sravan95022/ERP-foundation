from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.inventory import MovementType


class WarehouseCreate(BaseModel):
    name: str
    location: Optional[str] = None
    branch_id: Optional[int] = None


class WarehouseOut(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    class Config:
        from_attributes = True


class StockAdjust(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: Decimal  # positive to add, negative to remove
    movement_type: MovementType
    reference: Optional[str] = None
    batch_number: Optional[str] = None


class StockOut(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity: Decimal
    batch_number: Optional[str] = None
    updated_at: datetime
    class Config:
        from_attributes = True


class StockMovementOut(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    movement_type: MovementType
    quantity: Decimal
    reference: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


class ReconciliationResult(BaseModel):
    product_id: int
    warehouse_id: int
    stock_table_quantity: Decimal
    movements_sum: Decimal
    is_balanced: bool
