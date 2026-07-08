import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/api/v1/monitoring", tags=["Logging & Monitoring"])

_start_time = time.time()
_request_count = {"total": 0}


@router.get("/health-detailed")
def health_detailed(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "uptime_seconds": round(time.time() - _start_time, 1),
    }


@router.get("/metrics")
def metrics():
    """Basic metrics endpoint — swap for a Prometheus exporter in production."""
    return {
        "uptime_seconds": round(time.time() - _start_time, 1),
        "requests_served": _request_count["total"],
    }
