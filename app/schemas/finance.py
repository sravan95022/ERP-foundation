from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.models.finance import AccountType


class AccountOut(BaseModel):
    code: str
    name: str
    account_type: AccountType
    class Config:
        from_attributes = True


class TrialBalanceRow(BaseModel):
    code: str
    name: str
    type: AccountType
    total_debit: Decimal
    total_credit: Decimal
    balance: Decimal
