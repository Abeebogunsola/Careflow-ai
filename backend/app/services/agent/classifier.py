"""
Intent and Barrier Classifier for CareFlow AI.

Source of truth: docs/ai-agent-specification.md - Sections 6, 7, 8, 9
and docs/database-design.md - Section 17.
"""

import re
from typing import Tuple, Optional
from app.models.enums import AIIntentCategory
from app.services.agent.guardrails import (
    check_emergency,
    check_medication_concern,
    check_clinical_concern,
)

# ------------------------------------------------------------------------------
# Pattern Definitions
# ------------------------------------------------------------------------------
HUMAN_STAFF_PATTERNS = [
    r"\b(speak|talk) to (someone|somebody|a human|a person|staff|a nurse|a doctor|a clinician)\b",
    r"\b(have|let) (a )?(nurse|doctor|staff member|someone|somebody) (from the clinic )?call me\b",
    r"\b(someone|somebody|staff|nurse|doctor) (from the clinic )?call me\b",
    r"\bcall me (please|back)?\b",
    r"\bhuman assistance\b",
    r"\breal person\b",
    r"\brepresentative\b",
    r"\bconnect me to (staff|clinic|human)\b",
    r"\bneed to talk to (the )?clinic\b",
]


RESCHEDULING_PATTERNS = [
    r"\breschedul(e|ing)\b",
    r"\bchange (my )?(appointment|date|time|visit)\b",
    r"\bmove (my )?(appointment|visit)\b",
    r"\bcan('?t|not) (make it|attend|come) (to |my |tomorrow|next week)?\b",
    r"\bpostpone (my )?(appointment|visit)\b",
    r"\banother (day|date|time)\b",
    r"\bdifferent (day|date|time)\b",
]

BARRIER_PATTERNS = {
    "transportation": [
        r"\btransport(ation)?\b",
        r"\bno (ride|car|bus|cab|fare)\b",
        r"\bcannot afford (the )?(bus|ride|taxi|fare)\b",
        r"\bcar broke down\b",
        r"\btoo far to travel\b",
        r"\bno way to get there\b",
    ],
    "work_schedule": [
        r"\bwork (conflict|shift|hours|schedule)\b",
        r"\bat work\b",
        r"\bboss won'?t let me\b",
        r"\bcannot take time off\b",
        r"\bworking (late|overtime|that day)\b",
    ],
    "financial_logistical": [
        r"\bno money\b",
        r"\bcannot afford\b",
        r"\bfinancial (hardship|problem|issues?)\b",
        r"\bfunds\b",
    ],
    "communication_difficulty": [
        r"\bphone was off\b",
        r"\blost my phone\b",
        r"\bno (signal|service|minutes|airtime)\b",
        r"\bcould not reach you\b",
    ],
    "clinic_access": [
        r"\bclinic was closed\b",
        r"\bcould not find (the )?clinic\b",
        r"\bdifficulty reaching the facility\b",
    ],
}

APPOINTMENT_ASSISTANCE_PATTERNS = [
    r"\bwhen is my (next )?(appointment|visit)\b",
    r"\bwhat time is my (appointment|visit)\b",
    r"\bwhere is my (appointment|visit)\b",
    r"\bcheck my appointment\b",
    r"\bappointment (date|time|details|schedule)\b",
    r"\bdo i have an appointment\b",
]

GENERAL_SUPPORT_PATTERNS = [
    r"\b(clinic )?hours\b",
    r"\boperating hours\b",
    r"\bopening (time|hours)\b",
    r"\bclinic location\b",
    r"\bwhat services\b",
    r"\bclinic open\b",
    r"\bprogram information\b",
    r"\bgeneral (support|question|inquiry)\b",
    r"\bi need help\b",
    r"\bcontact information\b",
]


def classify_message(text: str) -> Tuple[AIIntentCategory, Optional[str]]:
    """
    Classifies an incoming client message into one of 9 intent categories
    and detects non-clinical barrier subtypes where applicable.

    Priority hierarchy follows docs/ai-agent-specification.md:
    1. Emergency
    2. Medication concern
    3. Clinical concern
    4. Human staff request
    5. Rescheduling
    6. Barrier to care
    7. Appointment assistance
    8. General support
    9. Unknown
    """
    cleaned = text.strip()
    lower = cleaned.lower()

    if not cleaned:
        return AIIntentCategory.UNKNOWN, None

    # 1. Emergency Check (Highest priority)
    if check_emergency(lower):
        return AIIntentCategory.EMERGENCY_RELATED, None

    # 2. Medication Concern Check
    if check_medication_concern(lower):
        return AIIntentCategory.MEDICATION_CONCERN, None

    # 3. Clinical Concern Check
    if check_clinical_concern(lower):
        return AIIntentCategory.CLINICAL_CONCERN, None

    # 4. Human Staff Request
    for pattern in HUMAN_STAFF_PATTERNS:
        if re.search(pattern, lower):
            return AIIntentCategory.HUMAN_STAFF_REQUEST, None

    # 5. Barrier Check
    for barrier_type, patterns in BARRIER_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return AIIntentCategory.BARRIER_TO_CARE, barrier_type

    # 6. Rescheduling Check
    for pattern in RESCHEDULING_PATTERNS:
        if re.search(pattern, lower):
            return AIIntentCategory.RESCHEDULING, None

    # 7. Appointment Assistance Check
    for pattern in APPOINTMENT_ASSISTANCE_PATTERNS:
        if re.search(pattern, lower):
            return AIIntentCategory.APPOINTMENT_ASSISTANCE, None

    # 8. General Support Check
    for pattern in GENERAL_SUPPORT_PATTERNS:
        if re.search(pattern, lower):
            return AIIntentCategory.GENERAL_SUPPORT, None

    # 9. Fallback / Unknown Intent
    return AIIntentCategory.UNKNOWN, None
