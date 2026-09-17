"""
CommunicationPreference Model.

Source of truth: docs/database-design.md - Section 10. Table: `communication_preferences`
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.client import Client


class CommunicationPreference(Base):
    __tablename__ = "communication_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(50),
        default="web",
        nullable=False,
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # 1:1 relationship with Client
    client: Mapped["Client"] = relationship(
        "Client",
        back_populates="communication_preference",
    )

    def __repr__(self) -> str:
        return f"<CommunicationPreference(id={self.id}, client_id={self.client_id}, channel='{self.channel}')>"
