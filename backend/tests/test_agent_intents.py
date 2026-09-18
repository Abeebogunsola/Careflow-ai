"""
Intent and Barrier Classification Tests for CareFlow AI.

Source of truth: docs/ai-agent-specification.md - Sections 6, 7, 8, 9
and docs/database-design.md - Section 17.
"""

import pytest
from app.models.enums import AIIntentCategory
from app.services.agent.classifier import classify_message


@pytest.mark.parametrize(
    "message,expected_intent",
    [
        # Emergency
        ("I am having severe chest pain right now", AIIntentCategory.EMERGENCY_RELATED),
        ("Call 911 immediately, I took an overdose", AIIntentCategory.EMERGENCY_RELATED),
        # Medication Concern
        ("This medication makes me feel sick, should I stop taking it?", AIIntentCategory.MEDICATION_CONCERN),
        ("I missed my dose yesterday, should I double my dose?", AIIntentCategory.MEDICATION_CONCERN),
        # Clinical Concern
        ("Can you diagnose what condition causes my high fever?", AIIntentCategory.CLINICAL_CONCERN),
        ("Can you interpret my viral load lab results?", AIIntentCategory.CLINICAL_CONCERN),
        # Human Staff Request
        ("Please have a nurse call me back", AIIntentCategory.HUMAN_STAFF_REQUEST),
        ("I want to speak to someone at the clinic", AIIntentCategory.HUMAN_STAFF_REQUEST),
        ("Can I talk to a real person?", AIIntentCategory.HUMAN_STAFF_REQUEST),
        # Rescheduling
        ("I won't be able to make it tomorrow, can I reschedule?", AIIntentCategory.RESCHEDULING),
        ("Please change my appointment to next Monday", AIIntentCategory.RESCHEDULING),
        # Appointment Assistance
        ("When is my next appointment scheduled?", AIIntentCategory.APPOINTMENT_ASSISTANCE),
        ("Where is my appointment and what time?", AIIntentCategory.APPOINTMENT_ASSISTANCE),
        # General Support
        ("What are the clinic operating hours?", AIIntentCategory.GENERAL_SUPPORT),
        ("Can you tell me about the program information?", AIIntentCategory.GENERAL_SUPPORT),
        # Unknown Intent
        ("I don't know what to say", AIIntentCategory.UNKNOWN),
        ("xyz123 random text", AIIntentCategory.UNKNOWN),
        ("", AIIntentCategory.UNKNOWN),
    ],
)
def test_intent_classification(message, expected_intent):
    """Verifies all 9 intent categories are accurately classified."""
    intent, _ = classify_message(message)
    assert intent == expected_intent


@pytest.mark.parametrize(
    "message,expected_barrier",
    [
        ("I missed my appointment because I couldn't get transportation", "transportation"),
        ("I have no car and no ride to the clinic", "transportation"),
        ("I cannot attend due to a work shift conflict", "work_schedule"),
        ("I have no money right now and cannot afford to come", "financial_logistical"),
        ("My phone was off and I had no service", "communication_difficulty"),
        ("The clinic was closed when I arrived", "clinic_access"),
    ],
)
def test_barrier_classification(message, expected_barrier):
    """Verifies non-clinical barrier subtypes are detected correctly."""
    intent, barrier = classify_message(message)
    assert intent == AIIntentCategory.BARRIER_TO_CARE
    assert barrier == expected_barrier
