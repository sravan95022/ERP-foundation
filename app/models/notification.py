from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base


class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    channel = Column(String(20), nullable=False)  # email, sms, push, in_app
    template = Column(String(100), nullable=False)
    detail = Column(String(1000), nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)


TEMPLATES = {
    "approval_requested": "An item is awaiting your approval: {detail}",
    "password_reset": "Your password reset token: {detail}",
    "low_stock": "Stock alert: {detail}",
    "invoice_generated": "New invoice generated: {detail}",
}
