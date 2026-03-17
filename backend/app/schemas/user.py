"""Pydantic schemas for User resources."""
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from ..models.user import UserRole


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.driver

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user fields."""
    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    is_active: bool | None = None
    role: UserRole | None = None


class UserResponse(BaseModel):
    """Schema returned to API consumers."""
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """Internal schema that includes the hashed password."""
    hashed_password: str

    model_config = {"from_attributes": True}
