from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.crm import LeadStatus, OpportunityStage


class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None


class LeadOut(BaseModel):
    id: int
    name: str
    status: LeadStatus
    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    company_name: Optional[str] = None
    class Config:
        from_attributes = True


class OpportunityCreate(BaseModel):
    customer_id: int
    title: str
    value: Optional[Decimal] = None


class OpportunityOut(BaseModel):
    id: int
    customer_id: int
    title: str
    value: Optional[Decimal] = None
    stage: OpportunityStage
    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    customer_id: int
    channel: str
    notes: Optional[str] = None


class InteractionOut(BaseModel):
    id: int
    customer_id: int
    channel: str
    notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True
