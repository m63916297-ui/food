from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    role: str = "client"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    avatar_url: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: str | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class EmailRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
