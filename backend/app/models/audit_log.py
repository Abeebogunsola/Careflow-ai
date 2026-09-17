"""
AuditLog Model.

Source of truth: docs/database-design.md - Section 26. Table: `audit_logs`
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Any, Dict, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
    )
    # Stored in database as column "metadata"
    # Mapped to attribute metadata_ to prevent collision with SQLAlchemy Base.metadata
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationship
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="audit_logs",
        foreign_keys=[user_id],
    )

    @property
    def event_metadata(self) -> Optional[Dict[str, Any]]:
        return self.metadata_

    @event_metadata.setter
    def event_metadata(self, val: Optional[Dict[str, Any]]) -> None:
        self.metadata_ = val

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', entity_type='{self.entity_type}')>"
