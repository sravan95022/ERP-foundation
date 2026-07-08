from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    class Config:
        from_attributes = True


class BrandCreate(BaseModel):
    name: str


class BrandOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    base_price: Decimal
    cost_price: Decimal
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    barcode: Optional[str] = None
    base_price: Decimal
    cost_price: Decimal
    image_url: Optional[str] = None
    is_active: bool
    class Config:
        from_attributes = True
