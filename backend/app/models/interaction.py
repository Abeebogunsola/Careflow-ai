"""
Interaction Model.

Source of truth: docs/database-design.md - Section 14. Table: `interactions`
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.client import Client


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    direction: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    interaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    intent_category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    message_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    client: Mapped["Client"] = relationship(
        "Client",
        back_populates="interactions",
    )

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, client_id={self.client_id}, type='{self.interaction_type}', direction='{self.direction}')>"
