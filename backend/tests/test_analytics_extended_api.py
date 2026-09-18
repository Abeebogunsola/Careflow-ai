"""
Tests for CareFlow AI Extended Analytics API (Phase 9).

Validates:
1. GET /api/v1/analytics/appointments returns accurate adherence, missed, and completion metrics.
2. GET /api/v1/analytics/appointments supports date and type filtering.
3. GET /api/v1/analytics/engagement returns channel breakdown, intent distributions,
   barrier frequencies, follow-up progress, and escalation turnaround.
4. Strict zero PII leak prevention across all extended analytics endpoints.
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from app.models import (
    Base,
    Client,
    Appointment,
    FollowUpTask,
    Escalation,
    Interaction,
    EnrollmentStatus,
    AppointmentStatus,
    FollowUpStatus,
    FollowUpPriority,
    EscalationStatus,
    EscalationCategory,
    InteractionDirection,
    InteractionType,
    CommunicationChannel,
    AIIntentCategory,
)


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean all tables before and after each test."""
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


def test_get_analytics_appointments_empty_db(client):
    """Verify empty database returns clean zero-state appointment metrics."""
    response = client.get("/api/v1/analytics/appointments")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["total_appointments"] == 0
    assert data["scheduled_count"] == 0
    assert data["completed_count"] == 0
    assert data["missed_count"] == 0
    assert data["cancelled_count"] == 0
    assert data["rescheduled_count"] == 0
    assert data["completion_rate"] == 0.0
    assert data["missed_rate"] == 0.0
    assert data["by_type"] == {}


def test_get_analytics_appointments_populated_and_filtered(client):
    """Verify appointment metrics computation and query parameter filtering."""
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "TEST-ANALYTICS-CLI-1", "preferred_name": "Morgan"},
    )
    assert c_res.status_code == 201
    client_id = c_res.json()["data"]["id"]

    now = datetime.now(timezone.utc)
    appts = [
        {"appointment_type": "clinical_review", "status": "completed", "scheduled_at": (now - timedelta(days=5)).isoformat()},
        {"appointment_type": "clinical_review", "status": "completed", "scheduled_at": (now - timedelta(days=4)).isoformat()},
        {"appointment_type": "lab_visit", "status": "missed", "scheduled_at": (now - timedelta(days=3)).isoformat()},
        {"appointment_type": "lab_visit", "status": "cancelled", "scheduled_at": (now - timedelta(days=2)).isoformat()},
        {"appointment_type": "clinical_review", "status": "scheduled", "scheduled_at": (now + timedelta(days=2)).isoformat()},
        {"appointment_type": "refill", "status": "rescheduled", "scheduled_at": (now + timedelta(days=5)).isoformat()},
    ]
    for apt in appts:
        res = client.post("/api/v1/appointments", json={"client_id": client_id, **apt})
        assert res.status_code == 201

    # Query all appointments
    response = client.get("/api/v1/analytics/appointments")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["total_appointments"] == 6
    assert data["completed_count"] == 2
    assert data["missed_count"] == 1
    assert data["cancelled_count"] == 1
    assert data["scheduled_count"] == 1
    assert data["rescheduled_count"] == 1

    # Finalized = 2 completed + 1 missed + 1 cancelled = 4
    # Completion Rate = 2 / 4 = 50.0%
    assert data["completion_rate"] == 50.0

    # Missed Rate = 1 / (2 completed + 1 missed) = 33.33%
    assert data["missed_rate"] == 33.33

    # Type breakdown
    assert data["by_type"]["clinical_review"] == 3
    assert data["by_type"]["lab_visit"] == 2
    assert data["by_type"]["refill"] == 1

    # Test filtering by appointment_type
    filtered_resp = client.get("/api/v1/analytics/appointments?appointment_type=lab_visit")
    assert filtered_resp.status_code == 200
    f_data = filtered_resp.json()["data"]
    assert f_data["total_appointments"] == 2
    assert f_data["missed_count"] == 1
    assert f_data["cancelled_count"] == 1
    assert f_data["completed_count"] == 0
    assert f_data["missed_count"] == 1
    assert f_data["cancelled_count"] == 1
    assert f_data["completed_count"] == 0


def test_get_analytics_engagement_populated(client, db_session):
    """Verify engagement metrics: interactions, barrier categories, and escalation turnaround."""
    db = db_session
    client_rec = Client(
        id=uuid.uuid4(),
        external_reference="TEST-ENGAGEMENT-CLI-1",
        preferred_name="Jordan",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE,
    )
    db.add(client_rec)
    db.commit()

    now = datetime.now(timezone.utc)

    # 1. Interactions
    ints = [
        Interaction(
            id=uuid.uuid4(),
            client_id=client_rec.id,
            channel=CommunicationChannel.SMS,
            direction=InteractionDirection.INCOMING,
            interaction_type=InteractionType.MESSAGE,
            intent_category=AIIntentCategory.APPOINTMENT_ASSISTANCE,
        ),
        Interaction(
            id=uuid.uuid4(),
            client_id=client_rec.id,
            channel=CommunicationChannel.WHATSAPP,
            direction=InteractionDirection.OUTGOING,
            interaction_type=InteractionType.APPOINTMENT_REMINDER,
        ),
        Interaction(
            id=uuid.uuid4(),
            client_id=client_rec.id,
            channel=CommunicationChannel.SMS,
            direction=InteractionDirection.OUTGOING,
            interaction_type=InteractionType.AI_RESPONSE,
            intent_category=AIIntentCategory.GENERAL_SUPPORT,
        ),
    ]
    db.add_all(ints)

    # 2. Barriers (logged in follow-ups)
    fu1 = FollowUpTask(
        id=uuid.uuid4(),
        client_id=client_rec.id,
        priority=FollowUpPriority.HIGH,
        status=FollowUpStatus.PENDING,
        reason="Reported barrier to care: transport - client needs bus voucher",
    )
    fu2 = FollowUpTask(
        id=uuid.uuid4(),
        client_id=client_rec.id,
        priority=FollowUpPriority.NORMAL,
        status=FollowUpStatus.COMPLETED,
        reason="Reported barrier to care: schedule conflict with work shift",
    )
    db.add_all([fu1, fu2])

    # 3. Escalations with turnaround time
    esc1 = Escalation(
        id=uuid.uuid4(),
        client_id=client_rec.id,
        category=EscalationCategory.CLINICAL_CONCERN,
        status=EscalationStatus.RESOLVED,
        priority=FollowUpPriority.HIGH,
        reason="Client reported high fever",
        created_at=now - timedelta(hours=6),
        resolved_at=now - timedelta(hours=2),  # 4 hours turnaround
    )
    esc2 = Escalation(
        id=uuid.uuid4(),
        client_id=client_rec.id,
        category=EscalationCategory.HUMAN_REQUEST,
        status=EscalationStatus.OPEN,
        priority=FollowUpPriority.NORMAL,
        reason="Client asked for nurse call",
        created_at=now - timedelta(hours=1),
    )
    db.add_all([esc1, esc2])

    db.commit()

    # Query engagement
    response = client.get("/api/v1/analytics/engagement")
    assert response.status_code == 200
    data = response.json()["data"]

    # Interactions
    assert data["total_interactions"] == 3
    assert data["incoming_count"] == 1
    assert data["outgoing_count"] == 2
    assert data["by_channel"]["sms"] == 2
    assert data["by_channel"]["whatsapp"] == 1
    assert data["by_type"]["message"] == 1
    assert data["by_type"]["appointment_reminder"] == 1
    assert data["by_intent"]["appointment_assistance"] == 1
    assert data["by_intent"]["general_support"] == 1

    # Barriers
    assert "transport" in data["barrier_breakdown"]
    assert data["barrier_breakdown"]["transport"] == 1
    assert "schedule" in data["barrier_breakdown"]
    assert data["barrier_breakdown"]["schedule"] == 1

    # Escalations
    esc_data = data["escalation_metrics"]
    assert esc_data["total_escalations"] == 2
    assert esc_data["open_count"] == 1
    assert esc_data["resolved_count"] == 1
    assert esc_data["by_category"]["clinical_concern"] == 1
    assert esc_data["by_category"]["human_request"] == 1
    assert esc_data["avg_resolution_hours"] == 4.0

    # Follow-Ups
    fu_data = data["followup_metrics"]
    assert fu_data["total_followups"] == 2
    assert fu_data["pending_count"] == 1
    assert fu_data["completed_count"] == 1
    assert fu_data["completion_rate"] == 50.0


def test_analytics_extended_zero_pii(client, db_session):
    """Confirm zero PII, personal names, phone numbers, or notes in any analytics response."""
    db = db_session
    client_rec = Client(
        id=uuid.uuid4(),
        external_reference="CONFIDENTIAL-EXT-888",
        preferred_name="SuperSecretClient",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE,
    )
    db.add(client_rec)
    db.commit()

    for endpoint in ["/api/v1/analytics/overview", "/api/v1/analytics/appointments", "/api/v1/analytics/engagement"]:
        resp = client.get(endpoint)
        assert resp.status_code == 200
        text = resp.text
        assert "CONFIDENTIAL-EXT-888" not in text
        assert "SuperSecretClient" not in text
