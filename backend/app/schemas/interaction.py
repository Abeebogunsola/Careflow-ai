"""
Interaction Pydantic Schemas.

Source of truth: docs/api.md - Section 18 & docs/database-design.md - Section 14–17.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    CommunicationChannel,
    InteractionDirection,
    InteractionType,
    AIIntentCategory,
)


class InteractionBase(BaseModel):
    channel: CommunicationChannel = Field(
        ...,
        description="Communication channel (web, sms, whatsapp, email)",
    )
    direction: InteractionDirection = Field(
        ...,
        description="Message direction (incoming, outgoing)",
    )
    interaction_type: InteractionType = Field(
        ...,
        description="Category of interaction (message, appointment_reminder, follow_up, staff_response, ai_response, system_event)",
    )
    intent_category: Optional[AIIntentCategory] = Field(
        default=None,
        description="Optional AI intent classification",
    )
    message_reference: Optional[str] = Field(
        default=None,
        max_length=255,
        description="External messaging provider message ID",
    )
    content: Optional[str] = Field(
        default=None,
        description="Non-sensitive message content",
    )


class InteractionCreate(InteractionBase):
    client_id: uuid.UUID = Field(..., description="ID of client participating in interaction")


class InteractionRead(InteractionBase):
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
