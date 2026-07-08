from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.notification import NotificationLog
from app.services.notification_service import notify

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification Platform"])


@router.post("/send")
def send_notification(channel: str, template: str, detail: str, to: str = "system", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    log = notify(db, user.tenant_id, channel, template, detail, to)
    return {"id": log.id, "channel": log.channel, "sent_at": log.sent_at}


@router.get("/")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(NotificationLog).filter(NotificationLog.tenant_id == user.tenant_id).order_by(NotificationLog.sent_at.desc()).limit(50).all()
    return [{"id": r.id, "channel": r.channel, "template": r.template, "detail": r.detail, "sent_at": r.sent_at} for r in rows]
