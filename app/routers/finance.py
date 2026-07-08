from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.finance import Account
from app.schemas.finance import AccountOut, TrialBalanceRow
from app.services import finance_service

router = APIRouter(prefix="/api/v1/finance", tags=["Finance & Accounting"])


@router.post("/accounts/init")
def init_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    finance_service.ensure_default_accounts(db, user.tenant_id)
    return {"message": "Default chart of accounts ready"}


@router.get("/accounts", response_model=List[AccountOut])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Account).filter(Account.tenant_id == user.tenant_id).all()


@router.get("/reports/trial-balance", response_model=List[TrialBalanceRow])
def trial_balance(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return finance_service.trial_balance(db, user.tenant_id)
