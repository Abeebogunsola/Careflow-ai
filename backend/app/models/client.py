"""
Client Model.

Source of truth: docs/database-design.md - Section 8. Table: `clients`
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.appointment import Appointment
    from app.models.interaction import Interaction
    from app.models.follow_up import FollowUpTask
    from app.models.escalation import Escalation
    from app.models.communication_preference import CommunicationPreference


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    external_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )
    preferred_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    preferred_language: Mapped[str] = mapped_column(
        String(50),
        default="en",
        nullable=False,
    )
    enrollment_status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships (1:N and 1:1)
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    follow_up_tasks: Mapped[List["FollowUpTask"]] = relationship(
        "FollowUpTask",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    escalations: Mapped[List["Escalation"]] = relationship(
        "Escalation",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    communication_preference: Mapped[Optional["CommunicationPreference"]] = relationship(
        "CommunicationPreference",
        back_populates="client",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def status(self) -> str:
        return self.enrollment_status

    @status.setter
    def status(self, val: str) -> None:
        self.enrollment_status = val

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, external_reference='{self.external_reference}', status='{self.enrollment_status}')>"
