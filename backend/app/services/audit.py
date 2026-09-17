"""
Audit Service for CareFlow AI.

Records non-sensitive event logs for accountability and traceability.
Source of truth: docs/api.md - Section 36 & docs/database-design.md - Section 26.
"""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Creates an append-only audit record in the database.
    Does not commit the session directly to allow enclosing transaction control.
    """
    audit_entry = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        metadata_=metadata,
    )
    db.add(audit_entry)
    return audit_entry
