from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository, RoleRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def register_user(db: Session, payload: UserRegister) -> User:
    tenant_repo = TenantRepository(db)
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)

    tenant = tenant_repo.get_by_slug(payload.tenant_slug)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found. Create a tenant first.")

    existing = user_repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = role_repo.get_by_name(payload.role_name)
    if not role:
        role = role_repo.create({"name": payload.role_name})

    user = user_repo.create({
        "tenant_id": tenant.id,
        "role_id": role.id,
        "full_name": payload.full_name,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
    })
    return user


def authenticate_user(db: Session, payload: UserLogin) -> User:
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(payload.email)

    if user and user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=423, detail="Account temporarily locked due to repeated failed logins")

    if not user or not verify_password(payload.password, user.hashed_password):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= 5:
                from datetime import timedelta
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user_repo.update(user, {"last_login": datetime.utcnow(), "failed_login_attempts": 0, "locked_until": None})
    return user


def issue_tokens(user: User) -> dict:
    access_token = create_access_token(
        subject=str(user.id), tenant_id=user.tenant_id, role=user.role.name
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_repo = UserRepository(db)
    user = user_repo.get(int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return issue_tokens(user)
