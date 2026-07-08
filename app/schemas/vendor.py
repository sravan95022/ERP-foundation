from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date


class VendorCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_or_tax_id: Optional[str] = None


class VendorOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    is_compliant: int
    is_active: int
    class Config:
        from_attributes = True


class VendorContractCreate(BaseModel):
    vendor_id: int
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contract_value: Optional[Decimal] = None


class VendorContractOut(BaseModel):
    id: int
    vendor_id: int
    title: str
    contract_value: Optional[Decimal] = None
    class Config:
        from_attributes = True


class VendorEvaluationCreate(BaseModel):
    vendor_id: int
    rating: Decimal
    remarks: Optional[str] = None


class VendorEvaluationOut(BaseModel):
    id: int
    vendor_id: int
    rating: Optional[Decimal] = None
    class Config:
        from_attributes = True
