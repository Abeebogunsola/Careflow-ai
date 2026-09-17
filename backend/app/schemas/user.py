"""
User and Role Pydantic Schemas.

Source of truth: docs/database-design.md - Section 6 & 7.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoleRead(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: str = Field(
        ...,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Unique email address for user login",
    )
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    role_id: uuid.UUID = Field(..., description="Role ID assigned to user")
    password: str = Field(..., min_length=8, description="Initial plain text password to be securely hashed")


class UserRead(UserBase):
    id: uuid.UUID
    role_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # CRITICAL: password_hash is never exposed in response
    model_config = ConfigDict(from_attributes=True)
