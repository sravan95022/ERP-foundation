from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.repositories.tenant_repository import TenantRepository

router = APIRouter(prefix="/api/v1/tenants", tags=["Tenants"])


class TenantCreate(BaseModel):
    name: str
    slug: str


class TenantOut(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/", response_model=TenantOut, status_code=201)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    repo = TenantRepository(db)
    if repo.get_by_slug(payload.slug):
        raise HTTPException(status_code=400, detail="Tenant slug already exists")

    return repo.create({"name": payload.name, "slug": payload.slug})


@router.get("/", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    repo = TenantRepository(db)
    return repo.get_all()
