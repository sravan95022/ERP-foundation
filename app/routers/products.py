from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User
from app.models.product import Category, Brand, Product
from app.schemas.product import (
    CategoryCreate, CategoryOut, BrandCreate, BrandOut,
    ProductCreate, ProductUpdate, ProductOut,
)

router = APIRouter(prefix="/api/v1/products", tags=["Product Management"])


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = Category(tenant_id=user.tenant_id, name=payload.name, parent_id=payload.parent_id)
    db.add(cat); db.commit(); db.refresh(cat)
    return cat


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Category).filter(Category.tenant_id == user.tenant_id).all()


@router.post("/brands", response_model=BrandOut, status_code=201)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    brand = Brand(tenant_id=user.tenant_id, name=payload.name)
    db.add(brand); db.commit(); db.refresh(brand)
    return brand


@router.get("/brands", response_model=List[BrandOut])
def list_brands(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Brand).filter(Brand.tenant_id == user.tenant_id).all()


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    product = Product(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(product); db.commit(); db.refresh(product)
    return product


@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Product).filter(Product.tenant_id == user.tenant_id).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.tenant_id == user.tenant_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.tenant_id == user.tenant_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(product, k, v)
    db.commit(); db.refresh(product)
    return product
