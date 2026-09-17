"""
ApprovedInformation Pydantic Schemas.

Source of truth: docs/api.md - Section 24 & docs/database-design.md - Section 24 & 25.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApprovedInfoCategory


class ApprovedInformationBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Title of the approved information item",
    )
    category: ApprovedInfoCategory = Field(
        ...,
        description="Approved category (appointment_information, clinic_logistics, communication, program_information, approved_education)",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Authorized and vetted text content",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Information revision version number",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this information is active and retrievable by the AI support agent",
    )


class ApprovedInformationCreate(ApprovedInformationBase):
    pass


class ApprovedInformationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    category: Optional[ApprovedInfoCategory] = None
    content: Optional[str] = Field(default=None, min_length=1)
    version: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None


class ApprovedInformationRead(ApprovedInformationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
