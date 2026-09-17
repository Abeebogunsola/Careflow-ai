"""
Escalation Pydantic Schemas.

Source of truth: docs/api.md - Section 22 & docs/database-design.md - Section 21–23.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FollowUpPriority, EscalationCategory, EscalationStatus


class EscalationBase(BaseModel):
    category: EscalationCategory = Field(
        ...,
        description="Escalation category (clinical_concern, medication_concern, sensitive_concern, human_request, emergency_related, unknown_intent, ai_uncertainty, system_failure)",
    )
    priority: FollowUpPriority = Field(
        default=FollowUpPriority.HIGH,
        description="Priority of the escalation (normal, high, urgent)",
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Reason for escalation requiring human intervention",
    )
    status: EscalationStatus = Field(
        default=EscalationStatus.OPEN,
        description="Current escalation status (open, assigned, in_review, resolved, cancelled)",
    )


class EscalationCreate(EscalationBase):
    client_id: uuid.UUID = Field(..., description="ID of client involved in escalation")
    assigned_to: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional staff user ID assigned to review escalation",
    )


class EscalationUpdate(BaseModel):
    category: Optional[EscalationCategory] = None
    priority: Optional[FollowUpPriority] = None
    reason: Optional[str] = Field(default=None, min_length=1)
    status: Optional[EscalationStatus] = None
    assigned_to: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None


class EscalationRead(EscalationBase):
    id: uuid.UUID
    client_id: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
