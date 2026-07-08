from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.crm import Lead, Customer, Opportunity, Interaction, LeadStatus
from app.schemas.crm import (
    LeadCreate, LeadOut, CustomerCreate, CustomerOut,
    OpportunityCreate, OpportunityOut, InteractionCreate, InteractionOut,
)

router = APIRouter(prefix="/api/v1/crm", tags=["Customer & CRM"])


@router.post("/leads", response_model=LeadOut, status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lead = Lead(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(lead); db.commit(); db.refresh(lead)
    return lead


@router.get("/leads", response_model=List[LeadOut])
def list_leads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Lead).filter(Lead.tenant_id == user.tenant_id).all()


@router.post("/leads/{lead_id}/convert", response_model=CustomerOut)
def convert_lead(lead_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == user.tenant_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.status == LeadStatus.CONVERTED:
        raise HTTPException(status_code=400, detail="Lead already converted")

    customer = Customer(tenant_id=user.tenant_id, name=lead.name, email=lead.email, phone=lead.phone)
    db.add(customer)
    lead.status = LeadStatus.CONVERTED
    db.commit(); db.refresh(customer)
    return customer


@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    customer = Customer(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(customer); db.commit(); db.refresh(customer)
    return customer


@router.get("/customers", response_model=List[CustomerOut])
def list_customers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Customer).filter(Customer.tenant_id == user.tenant_id).all()


@router.post("/opportunities", response_model=OpportunityOut, status_code=201)
def create_opportunity(payload: OpportunityCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    opp = Opportunity(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(opp); db.commit(); db.refresh(opp)
    return opp


@router.get("/opportunities", response_model=List[OpportunityOut])
def list_opportunities(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Opportunity).filter(Opportunity.tenant_id == user.tenant_id).all()


@router.post("/interactions", response_model=InteractionOut, status_code=201)
def log_interaction(payload: InteractionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    interaction = Interaction(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(interaction); db.commit(); db.refresh(interaction)
    return interaction


@router.get("/customers/{customer_id}/interactions", response_model=List[InteractionOut])
def get_customer_interactions(customer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Interaction).filter(Interaction.customer_id == customer_id, Interaction.tenant_id == user.tenant_id).all()
