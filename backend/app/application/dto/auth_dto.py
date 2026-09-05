from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserResponseDto(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime


class TokenResponseDto(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponseDto


class RegisterRequestDto(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, max_length=150)
    setup_token: str


class LoginRequestDto(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequestDto(BaseModel):
    refresh_token: str
