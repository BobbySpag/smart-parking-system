"""Pydantic schemas for authentication."""
from pydantic import BaseModel, EmailStr
from ..models.user import UserRole


class Token(BaseModel):
    """JWT access token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded inside a JWT token."""
    sub: str | None = None
    role: UserRole | None = None


class LoginRequest(BaseModel):
    """Schema for JSON-based login requests."""
    email: EmailStr
    password: str
