from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.user import (
    ProfileUpdate, PreferencesUpdate, UserProfileOut,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    ActivityLogOut,
)
from app.services import user_service

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])


@router.get("/me/profile", response_model=UserProfileOut)
def get_my_profile(user: User = Depends(get_current_user)):
    return user


@router.put("/me/profile", response_model=UserProfileOut)
def update_my_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.update_profile(db, user, payload)


@router.put("/me/preferences", response_model=UserProfileOut)
def update_my_preferences(
    payload: PreferencesUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.update_preferences(db, user, payload)


@router.post("/me/change-password", status_code=204)
def change_my_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_service.change_password(db, user, payload.current_password, payload.new_password)


@router.get("/me/activity", response_model=List[ActivityLogOut])
def my_activity(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.get_activity_log(db, user.id)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    token = user_service.request_password_reset(db, payload.email)
    # Returned directly for now since Notifications (email) isn't built yet.
    return {"message": "If that email exists, a reset token has been issued.", "reset_token": token}


@router.post("/reset-password", status_code=204)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user_service.reset_password(db, payload.token, payload.new_password)


@router.post("/{user_id}/deactivate", response_model=UserProfileOut)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    from app.repositories.user_repository import UserRepository
    target = UserRepository(db).get(user_id)
    if not target:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user_service.deactivate_account(db, target)


@router.post("/{user_id}/reactivate", response_model=UserProfileOut)
def reactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    from app.repositories.user_repository import UserRepository
    target = UserRepository(db).get(user_id)
    if not target:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user_service.reactivate_account(db, target)
