from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.workflow import ApprovalRequest
from app.services import workflow_service

router = APIRouter(prefix="/api/v1/workflow", tags=["Workflow Engine"])


@router.post("/approvals")
def create_approval(entity_type: str, entity_id: int, approver_role: str = "admin", sla_hours: int = 24, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    req = workflow_service.create_approval(db, user.tenant_id, user.id, entity_type, entity_id, approver_role, sla_hours)
    return {"id": req.id, "status": req.status, "entity_type": req.entity_type, "entity_id": req.entity_id}


@router.post("/approvals/{approval_id}/decide")
def decide(approval_id: int, approve: bool, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    req = workflow_service.resolve_approval(db, user.tenant_id, approval_id, approve)
    return {"id": req.id, "status": req.status}


@router.get("/approvals")
def list_approvals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == user.tenant_id).all()
    return [{"id": r.id, "entity_type": r.entity_type, "entity_id": r.entity_id, "status": r.status} for r in rows]


@router.post("/approvals/check-escalations")
def check_escalations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    escalated = workflow_service.check_and_escalate_overdue(db, user.tenant_id)
    return {"escalated_count": len(escalated)}
