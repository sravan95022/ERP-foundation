from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.crm import Customer
from app.models.vendor import Vendor
from app.models.search_log import SearchLog

router = APIRouter(prefix="/api/v1/search", tags=["Search Platform"])


@router.get("/")
def global_search(q: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    like = f"%{q}%"
    products = db.query(Product).filter(Product.tenant_id == user.tenant_id, Product.name.ilike(like)).limit(10).all()
    customers = db.query(Customer).filter(Customer.tenant_id == user.tenant_id, Customer.name.ilike(like)).limit(10).all()
    vendors = db.query(Vendor).filter(Vendor.tenant_id == user.tenant_id, Vendor.name.ilike(like)).limit(10).all()

    total = len(products) + len(customers) + len(vendors)
    db.add(SearchLog(tenant_id=user.tenant_id, query=q, result_count=total))
    db.commit()

    return {
        "products": [{"id": p.id, "name": p.name, "sku": p.sku} for p in products],
        "customers": [{"id": c.id, "name": c.name} for c in customers],
        "vendors": [{"id": v.id, "name": v.name} for v in vendors],
        "total_results": total,
    }


@router.get("/autocomplete")
def autocomplete(q: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    like = f"{q}%"
    names = [p.name for p in db.query(Product).filter(Product.tenant_id == user.tenant_id, Product.name.ilike(like)).limit(5).all()]
    return {"suggestions": names}


@router.get("/analytics")
def search_analytics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    logs = db.query(SearchLog).filter(SearchLog.tenant_id == user.tenant_id).order_by(SearchLog.created_at.desc()).limit(50).all()
    return [{"query": l.query, "result_count": l.result_count, "at": l.created_at} for l in logs]
