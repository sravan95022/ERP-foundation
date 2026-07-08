from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, RefreshRequest, UserOut
from app.services.auth_service import (
    register_user,
    authenticate_user,
    issue_tokens,
    refresh_access_token,
)
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, payload)
    return UserOut(
        id=user.id, full_name=user.full_name, email=user.email,
        role=user.role.name, tenant_id=user.tenant_id, is_active=user.is_active,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    return issue_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return refresh_access_token(db, payload.refresh_token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(
        id=user.id, full_name=user.full_name, email=user.email,
        role=user.role.name, tenant_id=user.tenant_id, is_active=user.is_active,
    )
