"""
Schemas Package for CareFlow AI.
"""

from app.schemas.common import (
    PaginationMeta,
    DataResponse,
    PaginatedResponse,
    ErrorDetail,
    ErrorResponse,
)
from app.schemas.client import ClientCreate, ClientUpdate, ClientRead
from app.schemas.communication_preference import (
    CommunicationPreferenceCreate,
    CommunicationPreferenceUpdate,
    CommunicationPreferenceRead,
)
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentRead
from app.schemas.interaction import InteractionCreate, InteractionRead
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate, FollowUpRead
from app.schemas.escalation import EscalationCreate, EscalationUpdate, EscalationRead
from app.schemas.approved_info import (
    ApprovedInformationCreate,
    ApprovedInformationUpdate,
    ApprovedInformationRead,
)
from app.schemas.audit_log import AuditLogRead
from app.schemas.user import RoleRead, UserCreate, UserRead

__all__ = [
    "PaginationMeta",
    "DataResponse",
    "PaginatedResponse",
    "ErrorDetail",
    "ErrorResponse",
    "ClientCreate",
    "ClientUpdate",
    "ClientRead",
    "CommunicationPreferenceCreate",
    "CommunicationPreferenceUpdate",
    "CommunicationPreferenceRead",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentRead",
    "InteractionCreate",
    "InteractionRead",
    "FollowUpCreate",
    "FollowUpUpdate",
    "FollowUpRead",
    "EscalationCreate",
    "EscalationUpdate",
    "EscalationRead",
    "ApprovedInformationCreate",
    "ApprovedInformationUpdate",
    "ApprovedInformationRead",
    "AuditLogRead",
    "RoleRead",
    "UserCreate",
    "UserRead",
]
