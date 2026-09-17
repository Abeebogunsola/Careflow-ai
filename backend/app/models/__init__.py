"""
Database Models Package for CareFlow AI.

Exposes all core domain models and enums per docs/database-design.md.
All models inherit from app.db.base.Base and register table metadata for Alembic.
"""

from app.db.base import Base
from app.models.role import Role
from app.models.user import User
from app.models.client import Client
from app.models.communication_preference import CommunicationPreference
from app.models.appointment import Appointment
from app.models.interaction import Interaction
from app.models.follow_up import FollowUpTask
from app.models.escalation import Escalation
from app.models.approved_info import ApprovedInformation
from app.models.audit_log import AuditLog
from app.models.enums import (
    RoleName,
    EnrollmentStatus,
    CommunicationChannel,
    AppointmentStatus,
    InteractionDirection,
    InteractionType,
    AIIntentCategory,
    FollowUpPriority,
    FollowUpStatus,
    EscalationCategory,
    EscalationStatus,
    ApprovedInfoCategory,
)

__all__ = [
    "Base",
    "Role",
    "User",
    "Client",
    "CommunicationPreference",
    "Appointment",
    "Interaction",
    "FollowUpTask",
    "Escalation",
    "ApprovedInformation",
    "AuditLog",
    "RoleName",
    "EnrollmentStatus",
    "CommunicationChannel",
    "AppointmentStatus",
    "InteractionDirection",
    "InteractionType",
    "AIIntentCategory",
    "FollowUpPriority",
    "FollowUpStatus",
    "EscalationCategory",
    "EscalationStatus",
    "ApprovedInfoCategory",
]
