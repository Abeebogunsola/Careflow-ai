"""
CommunicationPreference Pydantic Schemas.

Source of truth: docs/api.md & docs/database-design.md - Section 10.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models.enums import CommunicationChannel


class CommunicationPreferenceBase(BaseModel):
    channel: CommunicationChannel = Field(
        default=CommunicationChannel.WEB,
        description="Allowed communication channel (web, sms, whatsapp, email)",
    )
    is_enabled: bool = Field(
        default=True,
        description="Whether communication on this channel is permitted",
    )


class CommunicationPreferenceCreate(BaseModel):
    channel: Optional[CommunicationChannel] = Field(
        default=None,
        description="Allowed communication channel (web, sms, whatsapp, email)",
    )
    preferred_channel: Optional[CommunicationChannel] = Field(
        default=None,
        description="Alias for channel",
    )
    is_enabled: bool = Field(
        default=True,
        description="Whether communication on this channel is permitted",
    )


class CommunicationPreferenceUpdate(BaseModel):
    channel: Optional[CommunicationChannel] = None
    preferred_channel: Optional[CommunicationChannel] = None
    is_enabled: Optional[bool] = None


class CommunicationPreferenceRead(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    channel: str
    is_enabled: bool
    updated_at: datetime

    @computed_field
    @property
    def preferred_channel(self) -> str:
        return self.channel

    model_config = ConfigDict(
        from_attributes=True,
    )
