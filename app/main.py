from fastapi import FastAPI
from app.core.database import Base, engine
from app.core.rate_limit import RateLimitMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.logging_config import setup_logging
from app.core.scheduler import start_scheduler

# Import models so they register with Base metadata before create_all
from app.models import (
    organization, user, product, inventory, employee, crm, vendor,
    procurement, sales, order_processing, finance, workflow, notification,
    document, search_log, background_job, webhook, audit,
)  # noqa: F401

from app.routers import (
    auth, tenants, users, products, inventory as inventory_router, employees,
    crm as crm_router, vendors, procurement as procurement_router,
    sales as sales_router, order_processing as order_router, finance as finance_router,
    workflow as workflow_router, notifications, documents, search,
    reports, gateway, monitoring,
)

setup_logging()

app = FastAPI(
    title="Enterprise ERP System",
    description="Modular ERP platform covering Phases 1-31",
    version="0.3.0",
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

Base.metadata.create_all(bind=engine)

app.include_router(tenants.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(inventory_router.router)
app.include_router(employees.router)
app.include_router(crm_router.router)
app.include_router(vendors.router)
app.include_router(procurement_router.router)
app.include_router(sales_router.router)
app.include_router(order_router.router)
app.include_router(finance_router.router)
app.include_router(workflow_router.router)
app.include_router(notifications.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(reports.router)
app.include_router(gateway.router)
app.include_router(monitoring.router)


@app.on_event("startup")
def _on_startup():
    start_scheduler()


@app.get("/")
def root():
    return {"status": "ok", "message": "ERP System API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
