from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.workflow import ApprovalRequest, ApprovalStatus


def create_approval(db: Session, tenant_id: int, requested_by: int, entity_type: str, entity_id: int, approver_role: str = "admin", sla_hours: int = 24) -> ApprovalRequest:
    req = ApprovalRequest(
        tenant_id=tenant_id, entity_type=entity_type, entity_id=entity_id,
        requested_by=requested_by, approver_role=approver_role, sla_hours=sla_hours,
    )
    db.add(req); db.commit(); db.refresh(req)
    from app.services.notification_service import notify
    notify(db, tenant_id, channel="in_app", template="approval_requested",
           detail=f"{entity_type} #{entity_id} awaiting {approver_role} approval")
    return req


def resolve_approval(db: Session, tenant_id: int, approval_id: int, approve: bool) -> ApprovalRequest:
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id, ApprovalRequest.tenant_id == tenant_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")
    req.status = ApprovalStatus.APPROVED if approve else ApprovalStatus.REJECTED
    req.resolved_at = datetime.utcnow()
    db.commit(); db.refresh(req)
    return req


def check_and_escalate_overdue(db: Session, tenant_id: int) -> list:
    """Escalation check (SLA management) — call periodically from the
    Phase 27 background scheduler to flag approvals that missed their SLA."""
    pending = db.query(ApprovalRequest).filter(
        ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.status == ApprovalStatus.PENDING
    ).all()
    escalated = []
    for req in pending:
        if datetime.utcnow() > req.created_at + timedelta(hours=req.sla_hours):
            req.status = ApprovalStatus.ESCALATED
            escalated.append(req)
    if escalated:
        db.commit()
    return escalated
