from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.finance import Account, JournalEntry, JournalLine, AccountType

DEFAULT_ACCOUNTS = [
    ("1000", "Cash", AccountType.ASSET),
    ("1100", "Accounts Receivable", AccountType.ASSET),
    ("1200", "Inventory", AccountType.ASSET),
    ("2000", "Accounts Payable", AccountType.LIABILITY),
    ("4000", "Sales Revenue", AccountType.REVENUE),
    ("5000", "Cost of Goods Sold", AccountType.EXPENSE),
    ("5100", "Purchases", AccountType.EXPENSE),
]


def ensure_default_accounts(db: Session, tenant_id: int) -> None:
    existing = db.query(Account).filter(Account.tenant_id == tenant_id).count()
    if existing:
        return
    for code, name, atype in DEFAULT_ACCOUNTS:
        db.add(Account(tenant_id=tenant_id, code=code, name=name, account_type=atype))
    db.commit()


def get_account(db: Session, tenant_id: int, code: str) -> Account:
    acc = db.query(Account).filter(Account.tenant_id == tenant_id, Account.code == code).first()
    if not acc:
        raise HTTPException(status_code=500, detail=f"Account {code} not found — run ensure_default_accounts")
    return acc


def post_journal_entry(db: Session, tenant_id: int, reference: str, description: str, lines: list[dict]) -> JournalEntry:
    """lines: [{"account_code": "1100", "debit": 100, "credit": 0}, ...]
    Enforces the fundamental double-entry rule: total debits must equal total credits."""
    total_debit = sum(Decimal(str(l.get("debit", 0))) for l in lines)
    total_credit = sum(Decimal(str(l.get("credit", 0))) for l in lines)
    if total_debit != total_credit:
        raise HTTPException(status_code=400, detail=f"Unbalanced entry: debit={total_debit} credit={total_credit}")

    entry = JournalEntry(tenant_id=tenant_id, reference=reference, description=description)
    db.add(entry)
    db.flush()

    for l in lines:
        account = get_account(db, tenant_id, l["account_code"])
        db.add(JournalLine(
            tenant_id=tenant_id, entry_id=entry.id, account_id=account.id,
            debit=Decimal(str(l.get("debit", 0))), credit=Decimal(str(l.get("credit", 0))),
        ))
    db.commit()
    db.refresh(entry)
    return entry


def trial_balance(db: Session, tenant_id: int) -> list[dict]:
    rows = (
        db.query(
            Account.code, Account.name, Account.account_type,
            func.coalesce(func.sum(JournalLine.debit), 0).label("total_debit"),
            func.coalesce(func.sum(JournalLine.credit), 0).label("total_credit"),
        )
        .outerjoin(JournalLine, JournalLine.account_id == Account.id)
        .filter(Account.tenant_id == tenant_id)
        .group_by(Account.id)
        .all()
    )
    return [
        {
            "code": r.code, "name": r.name, "type": r.account_type,
            "total_debit": Decimal(str(r.total_debit)), "total_credit": Decimal(str(r.total_credit)),
            "balance": Decimal(str(r.total_debit)) - Decimal(str(r.total_credit)),
        }
        for r in rows
    ]
