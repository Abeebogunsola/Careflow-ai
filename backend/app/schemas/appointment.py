"""
Appointment Pydantic Schemas.

Source of truth: docs/api.md - Section 17 & docs/database-design.md - Section 11 & 12.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AppointmentStatus


class AppointmentBase(BaseModel):
    appointment_type: str = Field(
        default="routine_checkup",
        min_length=1,
        max_length=100,
        description="Appointment category (e.g. Routine Consultation, Lab Visit)",
    )
    scheduled_at: datetime = Field(
        ...,
        description="Scheduled appointment date and time in ISO 8601 format",
    )
    status: AppointmentStatus = Field(
        default=AppointmentStatus.SCHEDULED,
        description="Current appointment status (scheduled, completed, missed, cancelled, rescheduled)",
    )
    location_label: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Permitted non-sensitive clinic location label",
    )


class AppointmentCreate(AppointmentBase):
    client_id: uuid.UUID = Field(..., description="ID of the client for whom appointment is scheduled")


class AppointmentUpdate(BaseModel):
    appointment_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    scheduled_at: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    location_label: Optional[str] = Field(default=None, max_length=255)


class AppointmentRead(AppointmentBase):
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
