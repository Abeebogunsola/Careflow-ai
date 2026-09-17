"""
Client Pydantic Schemas.

Source of truth: docs/api.md - Section 16 & docs/database-design.md - Section 8 & 9.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EnrollmentStatus, CommunicationChannel


class ClientBase(BaseModel):
    external_reference: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Synthetic external reference identifier (e.g. CLIENT-0001)",
    )
    preferred_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Client preferred name or pseudonym",
    )
    preferred_language: str = Field(
        default="en",
        max_length=50,
        description="Preferred language code",
    )
    enrollment_status: EnrollmentStatus = Field(
        default=EnrollmentStatus.ACTIVE,
        description="Client program enrollment status",
    )
    status: Optional[EnrollmentStatus] = Field(
        default=None,
        description="Client status alias for enrollment_status per docs/api.md",
    )
    is_active: bool = Field(
        default=True,
        description="Whether client record is currently active",
    )


class ClientCreate(ClientBase):
    communication_channel: Optional[CommunicationChannel] = Field(
        default=None,
        description="Initial communication channel preference (optional upon creation)",
    )


class ClientUpdate(BaseModel):
    external_reference: Optional[str] = Field(default=None, max_length=100)
    preferred_name: Optional[str] = Field(default=None, max_length=100)
    preferred_language: Optional[str] = Field(default=None, max_length=50)
    enrollment_status: Optional[EnrollmentStatus] = None
    status: Optional[EnrollmentStatus] = None
    is_active: Optional[bool] = None


class ClientRead(ClientBase):
    id: uuid.UUID
    status: str = Field(
        default="active",
        description="Current client status",
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
