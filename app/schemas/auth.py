from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    tenant_slug: str = Field(..., description="Slug of the tenant/organization signing up")
    full_name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    role_name: str = Field(default="employee")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    tenant_id: int
    is_active: bool

    class Config:
        from_attributes = True
