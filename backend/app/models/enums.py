"""
Enum Definitions for CareFlow AI Database Entities.

Source of truth: docs/database-design.md
"""

from enum import Enum


class RoleName(str, Enum):
    CLIENT = "client"
    STAFF = "staff"
    ADMIN = "admin"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class CommunicationChannel(str, Enum):
    WEB = "web"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class InteractionDirection(str, Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class InteractionType(str, Enum):
    MESSAGE = "message"
    APPOINTMENT_REMINDER = "appointment_reminder"
    FOLLOW_UP = "follow_up"
    STAFF_RESPONSE = "staff_response"
    AI_RESPONSE = "ai_response"
    SYSTEM_EVENT = "system_event"


class AIIntentCategory(str, Enum):
    APPOINTMENT_ASSISTANCE = "appointment_assistance"
    RESCHEDULING = "rescheduling"
    GENERAL_SUPPORT = "general_support"
    BARRIER_TO_CARE = "barrier_to_care"
    HUMAN_STAFF_REQUEST = "human_staff_request"
    CLINICAL_CONCERN = "clinical_concern"
    MEDICATION_CONCERN = "medication_concern"
    EMERGENCY_RELATED = "emergency_related"
    UNKNOWN = "unknown"


class FollowUpPriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class FollowUpStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EscalationCategory(str, Enum):
    CLINICAL_CONCERN = "clinical_concern"
    MEDICATION_CONCERN = "medication_concern"
    SENSITIVE_CONCERN = "sensitive_concern"
    HUMAN_REQUEST = "human_request"
    EMERGENCY_RELATED = "emergency_related"
    UNKNOWN_INTENT = "unknown_intent"
    AI_UNCERTAINTY = "ai_uncertainty"
    SYSTEM_FAILURE = "system_failure"


class EscalationStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class ApprovedInfoCategory(str, Enum):
    APPOINTMENT_INFORMATION = "appointment_information"
    CLINIC_LOGISTICS = "clinic_logistics"
    COMMUNICATION = "communication"
    PROGRAM_INFORMATION = "program_information"
    APPROVED_EDUCATION = "approved_education"
