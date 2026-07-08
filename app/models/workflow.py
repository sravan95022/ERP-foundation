from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from datetime import datetime
import enum
from app.core.database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ApprovalRequest(Base):
    """Generic, reusable approval workflow — any module can create one by
    pointing entity_type/entity_id at its own record (e.g. 'purchase_request', 5)."""
    __tablename__ = "approval_requests"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_role = Column(String(50), nullable=False, default="admin")
    sla_hours = Column(Integer, default=24)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
