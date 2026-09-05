from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Senha com no mínimo 8 caracteres",
    )
    full_name: str | None = Field(
        default=None,
        max_length=150,
        description="Nome completo do usuário",
    )
    setup_token: str = Field(
        description="Token administrativo definido em SETUP_TOKEN",
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = Field(
        default=None,
        description="Refresh token. Opcional na Web quando enviado via cookie HttpOnly.",
    )


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(
        default=None,
        description="Refresh token. Opcional na Web quando enviado via cookie HttpOnly.",
    )


class StatusResponse(BaseModel):
    status: str
