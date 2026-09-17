"""
AuditLog Pydantic Schemas.

Source of truth: docs/api.md - Section 36 & docs/database-design.md - Section 26 & 27.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class AuditLogRead(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = Field(default=None, description="User who triggered action, if applicable")
    action: str = Field(..., description="Action name (e.g. client_created, escalation_created)")
    entity_type: str = Field(..., description="Target entity type (e.g. client, appointment)")
    entity_id: Optional[uuid.UUID] = Field(default=None, description="Target entity UUID")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="metadata_",
        description="Non-sensitive metadata associated with event",
    )
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
