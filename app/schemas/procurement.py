from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.models.procurement import PRStatus, POStatus


class PRCreate(BaseModel):
    product_id: int
    quantity: Decimal


class PROut(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    status: PRStatus
    class Config:
        from_attributes = True


class POConvert(BaseModel):
    vendor_id: int
    warehouse_id: int
    unit_price: Decimal


class POOut(BaseModel):
    id: int
    po_number: str
    vendor_id: int
    quantity_ordered: Decimal
    quantity_received: Decimal
    status: POStatus
    class Config:
        from_attributes = True


class GoodsReceiptCreate(BaseModel):
    purchase_order_id: int
    quantity: Decimal


class GoodsReceiptOut(BaseModel):
    id: int
    purchase_order_id: int
    quantity_received: Decimal
    class Config:
        from_attributes = True


class VendorPaymentCreate(BaseModel):
    purchase_order_id: int
    amount: Decimal


class VendorPaymentOut(BaseModel):
    id: int
    purchase_order_id: int
    amount: Decimal
    class Config:
        from_attributes = True
