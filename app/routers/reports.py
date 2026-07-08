import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.sales import Invoice, SalesOrder
from app.models.procurement import PurchaseOrder
from app.models.inventory import Stock
from app.models.product import Product

router = APIRouter(prefix="/api/v1/reports", tags=["Reporting & Dashboard"])


@router.get("/sales")
def sales_report(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Dynamic report with drill-down via query params (extendable)."""
    invoices = db.query(Invoice).filter(Invoice.tenant_id == user.tenant_id).all()
    return {
        "invoice_count": len(invoices),
        "total_revenue": sum(float(i.total_amount) for i in invoices),
        "invoices": [{"invoice_number": i.invoice_number, "total": float(i.total_amount)} for i in invoices],
    }


@router.get("/sales/export.csv")
def export_sales_csv(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoices = db.query(Invoice).filter(Invoice.tenant_id == user.tenant_id).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["invoice_number", "subtotal", "discount", "tax", "total"])
    for i in invoices:
        writer.writerow([i.invoice_number, i.subtotal, i.discount_amount, i.tax_amount, i.total_amount])
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sales_report.csv"})


@router.get("/dashboard/executive")
def executive_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Phase 26: high-level KPIs for leadership."""
    total_revenue = db.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(Invoice.tenant_id == user.tenant_id).scalar()
    total_orders = db.query(func.count(SalesOrder.id)).filter(SalesOrder.tenant_id == user.tenant_id).scalar()
    total_pos = db.query(func.count(PurchaseOrder.id)).filter(PurchaseOrder.tenant_id == user.tenant_id).scalar()
    stock_value = db.query(func.coalesce(func.sum(Stock.quantity * Product.cost_price), 0)).join(Product, Product.id == Stock.product_id).filter(Stock.tenant_id == user.tenant_id).scalar()

    return {
        "total_revenue": float(total_revenue),
        "total_sales_orders": total_orders,
        "total_purchase_orders": total_pos,
        "current_stock_value": float(stock_value),
    }


@router.get("/dashboard/forecast")
def simple_forecast(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Naive forecast: average of past invoice totals projected forward.
    A placeholder for a real time-series model — good enough to demo the concept."""
    invoices = db.query(Invoice).filter(Invoice.tenant_id == user.tenant_id).all()
    if not invoices:
        return {"forecast_next_period_revenue": 0}
    avg = sum(float(i.total_amount) for i in invoices) / len(invoices)
    return {"forecast_next_period_revenue": round(avg, 2), "based_on_invoices": len(invoices)}
