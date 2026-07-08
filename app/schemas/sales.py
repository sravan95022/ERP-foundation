from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.models.sales import SOStatus


class SalesOrderCreate(BaseModel):
    customer_id: int
    product_id: int
    warehouse_id: int
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal = Decimal(0)
    tax_percent: Decimal = Decimal(0)


class SalesOrderOut(BaseModel):
    id: int
    order_number: str
    customer_id: int
    quantity: Decimal
    unit_price: Decimal
    status: SOStatus
    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    sales_order_id: int
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    class Config:
        from_attributes = True
