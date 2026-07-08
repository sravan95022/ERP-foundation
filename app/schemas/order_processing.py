from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.models.order_processing import ShipmentStatus


class ShipmentCreate(BaseModel):
    sales_order_id: int
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None


class ShipmentOut(BaseModel):
    id: int
    sales_order_id: int
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    status: ShipmentStatus
    class Config:
        from_attributes = True


class ReturnCreate(BaseModel):
    sales_order_id: int
    quantity: Decimal
    reason: Optional[str] = None


class ReturnOut(BaseModel):
    id: int
    sales_order_id: int
    quantity: Decimal
    class Config:
        from_attributes = True


class RefundCreate(BaseModel):
    return_request_id: int
    amount: Decimal


class RefundOut(BaseModel):
    id: int
    return_request_id: int
    amount: Decimal
    class Config:
        from_attributes = True
