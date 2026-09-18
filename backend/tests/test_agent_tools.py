"""
Controlled Agent Tool Tests for CareFlow AI.

Source of truth: docs/ai-agent-specification.md - Sections 10-18, 27
and docs/database-design.md.
"""

import uuid
from datetime import datetime, timezone, timedelta
from app.models import Client, Appointment, ApprovedInformation, AuditLog
from app.services.agent.tools import (
    get_client_profile,
    get_appointment,
    get_approved_information,
    create_followup,
    create_escalation,
    record_interaction,
)


def test_get_client_profile_minimization(db_session):
    """Profile retrieval must only return permitted non-sensitive fields."""
    client = Client(
        external_reference="SYNTH-MIN-001",
        preferred_name="Jordan",
        preferred_language="en",
        enrollment_status="active",
        is_active=True,
    )
    db_session.add(client)
    db_session.commit()

    profile = get_client_profile(db_session, client.id)
    assert profile is not None
    assert profile["preferred_name"] == "Jordan"
    assert profile["preferred_language"] == "en"
    assert profile["enrollment_status"] == "active"
    assert profile["is_active"] is True
    # Ensure no unrestricted fields or internal hashes are returned
    assert "password_hash" not in profile
    assert "notes" not in profile


def test_get_appointment_hallucination_resistance(db_session):
    """When no appointment exists, get_appointment returns None and never fabricates dates."""
    client = Client(
        external_reference="SYNTH-NOAPPT-001",
        preferred_name="Sam",
    )
    db_session.add(client)
    db_session.commit()

    appt = get_appointment(db_session, client.id)
    assert appt is None


def test_get_appointment_verified_upcoming(db_session):
    """get_appointment returns verified upcoming scheduled appointment details."""
    client = Client(
        external_reference="SYNTH-APPT-001",
        preferred_name="Taylor",
    )
    db_session.add(client)
    db_session.flush()

    sched_time = datetime.now(timezone.utc) + timedelta(days=2)
    appointment = Appointment(
        client_id=client.id,
        appointment_type="Routine Clinical Review",
        scheduled_at=sched_time,
        status="scheduled",
        location_label="Suite 3B - West Clinic",
    )
    db_session.add(appointment)
    db_session.commit()

    result = get_appointment(db_session, client.id)
    assert result is not None
    assert result["appointment_type"] == "Routine Clinical Review"
    assert result["status"] == "scheduled"
    assert result["location_label"] == "Suite 3B - West Clinic"


def test_get_approved_information_filters_inactive(db_session):
    """Tool returns only active approved information."""
    active_info = ApprovedInformation(
        title="Pharmacy Hours",
        category="clinic_logistics",
        content="Pharmacy open Monday to Friday 9am-4pm",
        version=1,
        is_active=True,
    )
    inactive_info = ApprovedInformation(
        title="Old Clinic Policy",
        category="clinic_logistics",
        content="Outdated hours",
        version=1,
        is_active=False,
    )
    db_session.add_all([active_info, inactive_info])
    db_session.commit()

    results = get_approved_information(db_session, category="clinic_logistics")
    assert len(results) == 1
    assert results[0]["title"] == "Pharmacy Hours"


def test_create_followup_records_audit(db_session):
    """Creating a follow-up task records a corresponding audit log."""
    client = Client(external_reference="SYNTH-FOL-002", preferred_name="Morgan")
    db_session.add(client)
    db_session.commit()

    task = create_followup(
        db=db_session,
        client_id=client.id,
        reason="Transportation barrier follow-up",
        priority="high",
    )
    db_session.commit()

    assert task.id is not None
    assert task.status == "pending"
    assert task.priority == "high"

    # Verify audit log was recorded
    audit = db_session.query(AuditLog).filter(AuditLog.entity_id == task.id).first()
    assert audit is not None
    assert audit.action == "followup_created"
    assert audit.entity_type == "follow_up_task"


def test_create_escalation_records_audit(db_session):
    """Creating an escalation records a corresponding audit log."""
    client = Client(external_reference="SYNTH-ESC-002", preferred_name="Casey")
    db_session.add(client)
    db_session.commit()

    esc = create_escalation(
        db=db_session,
        client_id=client.id,
        category="clinical_concern",
        priority="high",
        reason="Reported symptoms requiring nurse review",
    )
    db_session.commit()

    assert esc.id is not None
    assert esc.status == "open"

    audit = db_session.query(AuditLog).filter(AuditLog.entity_id == esc.id).first()
    assert audit is not None
    assert audit.action == "escalation_created"
    assert audit.entity_type == "escalation"
