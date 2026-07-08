from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.activity_repository import ActivityRepository
from app.schemas.user import ProfileUpdate, PreferencesUpdate
from app.core.security import hash_password, verify_password, generate_reset_token


def update_profile(db: Session, user: User, payload: ProfileUpdate) -> User:
    repo = UserRepository(db)
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    updated = repo.update(user, updates)
    ActivityRepository(db).log(user.id, "profile_update", detail=str(list(updates.keys())))
    return updated


def update_preferences(db: Session, user: User, payload: PreferencesUpdate) -> User:
    repo = UserRepository(db)
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    updated = repo.update(user, updates)
    ActivityRepository(db).log(user.id, "preferences_update", detail=str(list(updates.keys())))
    return updated


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    repo = UserRepository(db)
    repo.update(user, {"hashed_password": hash_password(new_password)})
    ActivityRepository(db).log(user.id, "password_change")


def request_password_reset(db: Session, email: str) -> str:
    """Returns the reset token. In production this would be emailed, not returned
    directly — returned here so the flow is testable end-to-end without an email
    provider wired up yet (Phase 9 - Notifications module)."""
    repo = UserRepository(db)
    user = repo.get_by_email(email)
    if not user:
        # Deliberately don't reveal whether the email exists.
        return "if-that-email-exists-a-reset-link-has-been-sent"

    token = generate_reset_token()
    repo.update(user, {
        "reset_token": token,
        "reset_token_expires": datetime.utcnow() + timedelta(hours=1),
    })
    ActivityRepository(db).log(user.id, "password_reset_requested")
    return token


def reset_password(db: Session, token: str, new_password: str) -> None:
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    repo = UserRepository(db)
    repo.update(user, {
        "hashed_password": hash_password(new_password),
        "reset_token": None,
        "reset_token_expires": None,
    })
    ActivityRepository(db).log(user.id, "password_reset_completed")


def deactivate_account(db: Session, user: User) -> User:
    repo = UserRepository(db)
    updated = repo.update(user, {"is_active": False, "deactivated_at": datetime.utcnow()})
    ActivityRepository(db).log(user.id, "account_deactivated")
    return updated


def reactivate_account(db: Session, user: User) -> User:
    repo = UserRepository(db)
    updated = repo.update(user, {"is_active": True, "deactivated_at": None})
    ActivityRepository(db).log(user.id, "account_reactivated")
    return updated


def get_activity_log(db: Session, user_id: int, limit: int = 50):
    return ActivityRepository(db).get_for_user(user_id, limit)
