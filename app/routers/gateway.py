from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.webhook import Webhook

router = APIRouter(prefix="/api/v1/gateway", tags=["API Gateway & Integrations"])


@router.get("/version")
def api_version():
    return {"current_version": "v1", "docs": "/docs", "openapi": "/openapi.json"}


@router.post("/webhooks")
def register_webhook(event_type: str, target_url: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    wh = Webhook(tenant_id=user.tenant_id, event_type=event_type, target_url=target_url)
    db.add(wh); db.commit(); db.refresh(wh)
    return {"id": wh.id, "event_type": wh.event_type, "target_url": wh.target_url}


@router.get("/webhooks")
def list_webhooks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Webhook).filter(Webhook.tenant_id == user.tenant_id).all()
    return [{"id": w.id, "event_type": w.event_type, "target_url": w.target_url, "is_active": w.is_active} for w in rows]
