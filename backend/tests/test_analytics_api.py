"""
Tests for CareFlow AI Analytics Endpoint (Phase 8).

Validates:
1. GET /api/v1/analytics/overview returns valid aggregate metrics on an empty database.
2. GET /api/v1/analytics/overview accurately reflects active clients, appointments,
   follow-ups, escalations, and interactions.
3. GET /api/v1/analytics/overview strictly exposes zero PII or individual-level data.
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


def test_get_analytics_overview_empty_db(client):
    """Verify that analytics overview returns zero counts when database is empty."""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200

    body = response.json()
    assert "data" in body
    data = body["data"]

    assert data["active_clients"] == 0
    assert data["appointments_scheduled"] == 0
    assert data["appointments_completed"] == 0
    assert data["appointments_missed"] == 0
    assert data["followups_pending"] == 0
    assert data["followups_completed"] == 0
    assert data["escalations_open"] == 0
    assert data["escalations_resolved"] == 0
    assert data["interactions_count"] == 0


def test_get_analytics_overview_populated(client, db_session):
    """Verify that aggregate counts accurately reflect database state."""
    db = db_session

    # 1. Clients (1 active, 1 inactive)
    active_client = Client(
        id=uuid.uuid4(),
        external_reference="CLIENT-ACT-001",
        preferred_name="ActiveUser",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE,
    )
    inactive_client = Client(
        id=uuid.uuid4(),
        external_reference="CLIENT-INACT-002",
        preferred_name="InactiveUser",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.INACTIVE,
    )
    db.add_all([active_client, inactive_client])
    db.commit()

    # 2. Appointments (1 scheduled, 1 completed, 1 missed)
    now = datetime.now(timezone.utc)
    appt1 = Appointment(
        id=uuid.uuid4(),
        client_id=active_client.id,
        scheduled_at=now + timedelta(days=1),
        appointment_type="routine_checkup",
        status=AppointmentStatus.SCHEDULED,
    )
    appt2 = Appointment(
        id=uuid.uuid4(),
        client_id=active_client.id,
        scheduled_at=now - timedelta(days=1),
        appointment_type="routine_checkup",
        status=AppointmentStatus.COMPLETED,
    )
    appt3 = Appointment(
        id=uuid.uuid4(),
        client_id=active_client.id,
        scheduled_at=now - timedelta(days=2),
        appointment_type="routine_checkup",
        status=AppointmentStatus.MISSED,
    )
    db.add_all([appt1, appt2, appt3])

    # 3. Follow-ups (1 pending, 1 completed)
    fu1 = FollowUpTask(
        id=uuid.uuid4(),
        client_id=active_client.id,
        priority=FollowUpPriority.NORMAL,
        status=FollowUpStatus.PENDING,
        reason="Check appointment attendance",
    )
    fu2 = FollowUpTask(
        id=uuid.uuid4(),
        client_id=active_client.id,
        priority=FollowUpPriority.NORMAL,
        status=FollowUpStatus.COMPLETED,
        reason="Assisted with transport barrier",
    )
    db.add_all([fu1, fu2])

    # 4. Escalations (1 open, 1 resolved)
    esc1 = Escalation(
        id=uuid.uuid4(),
        client_id=active_client.id,
        category=EscalationCategory.CLINICAL_CONCERN,
        status=EscalationStatus.OPEN,
        reason="Client reported fever and symptoms",
    )
    esc2 = Escalation(
        id=uuid.uuid4(),
        client_id=active_client.id,
        category=EscalationCategory.HUMAN_REQUEST,
        status=EscalationStatus.RESOLVED,
        reason="Requested nurse callback",
    )
    db.add_all([esc1, esc2])

    # 5. Interactions (2 total)
    int1 = Interaction(
        id=uuid.uuid4(),
        client_id=active_client.id,
        channel=CommunicationChannel.SMS,
        direction=InteractionDirection.INCOMING,
        interaction_type=InteractionType.MESSAGE,
    )
    int2 = Interaction(
        id=uuid.uuid4(),
        client_id=active_client.id,
        channel=CommunicationChannel.SMS,
        direction=InteractionDirection.OUTGOING,
        interaction_type=InteractionType.APPOINTMENT_REMINDER,
    )
    db.add_all([int1, int2])

    db.commit()

    # Query overview
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200

    body = response.json()
    assert "data" in body
    data = body["data"]

    assert data["active_clients"] == 1
    assert data["appointments_scheduled"] == 1
    assert data["appointments_completed"] == 1
    assert data["appointments_missed"] == 1
    assert data["followups_pending"] == 1
    assert data["followups_completed"] == 1
    assert data["escalations_open"] == 1
    assert data["escalations_resolved"] == 1
    assert data["interactions_count"] == 2


def test_analytics_overview_zero_pii(client, db_session):
    """Ensure response payload strictly contains aggregate numbers with no PII keys or sensitive details."""
    db = db_session
    client_rec = Client(
        id=uuid.uuid4(),
        external_reference="CONFIDENTIAL-REF-999",
        preferred_name="ConfidentialClient",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE,
    )
    db.add(client_rec)
    db.commit()

    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200

    response_text = response.text
    # Verify no PII appears anywhere in the response text
    assert "CONFIDENTIAL-REF-999" not in response_text
    assert "ConfidentialClient" not in response_text

    # Verify only approved aggregate keys are returned in data
    allowed_keys = {
        "active_clients",
        "appointments_scheduled",
        "appointments_completed",
        "appointments_missed",
        "followups_pending",
        "followups_completed",
        "escalations_open",
        "escalations_resolved",
        "interactions_count",
    }
    assert set(response.json()["data"].keys()) == allowed_keys
