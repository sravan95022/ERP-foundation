from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.vendor import Vendor, VendorContract, VendorEvaluation
from app.schemas.vendor import (
    VendorCreate, VendorOut, VendorContractCreate, VendorContractOut,
    VendorEvaluationCreate, VendorEvaluationOut,
)

router = APIRouter(prefix="/api/v1/vendors", tags=["Vendor & Supplier Management"])


@router.post("/", response_model=VendorOut, status_code=201)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vendor = Vendor(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(vendor); db.commit(); db.refresh(vendor)
    return vendor


@router.get("/", response_model=List[VendorOut])
def list_vendors(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Vendor).filter(Vendor.tenant_id == user.tenant_id).all()


@router.post("/contracts", response_model=VendorContractOut, status_code=201)
def create_contract(payload: VendorContractCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vendor = db.query(Vendor).filter(Vendor.id == payload.vendor_id, Vendor.tenant_id == user.tenant_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    contract = VendorContract(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(contract); db.commit(); db.refresh(contract)
    return contract


@router.get("/{vendor_id}/contracts", response_model=List[VendorContractOut])
def list_contracts(vendor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(VendorContract).filter(VendorContract.vendor_id == vendor_id, VendorContract.tenant_id == user.tenant_id).all()


@router.post("/evaluations", response_model=VendorEvaluationOut, status_code=201)
def add_evaluation(payload: VendorEvaluationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    evaluation = VendorEvaluation(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(evaluation); db.commit(); db.refresh(evaluation)
    return evaluation


@router.get("/{vendor_id}/evaluations", response_model=List[VendorEvaluationOut])
def list_evaluations(vendor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(VendorEvaluation).filter(VendorEvaluation.vendor_id == vendor_id, VendorEvaluation.tenant_id == user.tenant_id).all()
