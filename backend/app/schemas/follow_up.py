"""
FollowUpTask Pydantic Schemas.

Source of truth: docs/api.md - Section 21 & docs/database-design.md - Section 18–20.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FollowUpPriority, FollowUpStatus


class FollowUpBase(BaseModel):
    reason: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Reason for the follow-up task (e.g. Missed appointment follow-up)",
    )
    priority: FollowUpPriority = Field(
        default=FollowUpPriority.NORMAL,
        description="Follow-up priority level (normal, high, urgent)",
    )
    status: FollowUpStatus = Field(
        default=FollowUpStatus.PENDING,
        description="Current task status (pending, assigned, in_progress, completed, cancelled)",
    )
    due_at: Optional[datetime] = Field(
        default=None,
        description="Task due date and time",
    )


class FollowUpCreate(FollowUpBase):
    client_id: uuid.UUID = Field(..., description="ID of client requiring follow-up")
    assigned_to: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional staff user ID assigned to task",
    )


class FollowUpUpdate(BaseModel):
    reason: Optional[str] = Field(default=None, min_length=1, max_length=255)
    priority: Optional[FollowUpPriority] = None
    status: Optional[FollowUpStatus] = None
    assigned_to: Optional[uuid.UUID] = None
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class FollowUpRead(FollowUpBase):
    id: uuid.UUID
    client_id: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
