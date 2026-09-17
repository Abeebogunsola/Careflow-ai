"""
Database Model Tests for CareFlow AI.

Verifies SQLAlchemy models, relationships, constraints, UUID primary keys,
and timezone-aware timestamps according to docs/database-design.md.
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Base,
    Role,
    User,
    Client,
    CommunicationPreference,
    Appointment,
    Interaction,
    FollowUpTask,
    Escalation,
    ApprovedInformation,
    AuditLog,
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


def test_metadata_registers_all_ten_tables():
    """Verify that all 10 core tables are defined in Base.metadata."""
    expected_tables = {
        "roles",
        "users",
        "clients",
        "communication_preferences",
        "appointments",
        "interactions",
        "follow_up_tasks",
        "escalations",
        "approved_information",
        "audit_logs",
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables)


def test_create_role_and_user(db_session):
    """Test Role and User models, UUID primary keys, and relationships."""
    staff_role = Role(
        id=uuid.uuid4(),
        name=RoleName.STAFF.value,
        description="Authorized healthcare and program staff",
    )
    db_session.add(staff_role)
    db_session.flush()

    user = User(
        id=uuid.uuid4(),
        role_id=staff_role.id,
        email="staff.demo@example.test",
        password_hash="hashed_test_password_placeholder",
        first_name="Demo",
        last_name="Staff",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    # Verify retrieval and relationships
    retrieved_user = db_session.get(User, user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == "staff.demo@example.test"
    assert retrieved_user.role.name == RoleName.STAFF.value
    assert isinstance(retrieved_user.id, uuid.UUID)
    assert retrieved_user.created_at.tzinfo is not None


def test_unique_user_email_constraint(db_session):
    """Test that user email uniqueness constraint is enforced."""
    role = Role(name="admin_test", description="Test Admin")
    db_session.add(role)
    db_session.flush()

    user1 = User(
        role_id=role.id,
        email="duplicate@example.test",
        password_hash="hash1",
        first_name="Alice",
        last_name="Test",
    )
    user2 = User(
        role_id=role.id,
        email="duplicate@example.test",
        password_hash="hash2",
        first_name="Bob",
        last_name="Test",
    )
    db_session.add(user1)
    db_session.flush()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_client_and_communication_preference(db_session):
    """Test Client and 1:1 CommunicationPreference relationship."""
    client = Client(
        external_reference="CLIENT-SYNTH-001",
        preferred_name="Demo Client 001",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE.value,
        is_active=True,
    )
    db_session.add(client)
    db_session.flush()

    pref = CommunicationPreference(
        client_id=client.id,
        channel=CommunicationChannel.WEB.value,
        is_enabled=True,
    )
    db_session.add(pref)
    db_session.flush()

    retrieved = db_session.get(Client, client.id)
    assert retrieved.communication_preference is not None
    assert retrieved.communication_preference.channel == CommunicationChannel.WEB.value
    assert retrieved.communication_preference.client.id == client.id


def test_appointment_creation_and_query(db_session):
    """Test Appointment model, timezone-awareness, and client relationship."""
    client = Client(
        external_reference="CLIENT-SYNTH-002",
        preferred_name="Demo Client 002",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE.value,
    )
    db_session.add(client)
    db_session.flush()

    scheduled_time = datetime.now(timezone.utc) + timedelta(days=3)
    appointment = Appointment(
        client_id=client.id,
        appointment_type="Routine Consultation",
        scheduled_at=scheduled_time,
        status=AppointmentStatus.SCHEDULED.value,
        location_label="Clinic Room A",
    )
    db_session.add(appointment)
    db_session.flush()

    retrieved_app = db_session.get(Appointment, appointment.id)
    assert retrieved_app is not None
    assert retrieved_app.status == AppointmentStatus.SCHEDULED.value
    assert retrieved_app.scheduled_at == scheduled_time
    assert retrieved_app.client.id == client.id
    assert len(client.appointments) == 1


def test_interaction_creation(db_session):
    """Test Interaction model with intent classification."""
    client = Client(
        external_reference="CLIENT-SYNTH-003",
        preferred_name="Demo Client 003",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE.value,
    )
    db_session.add(client)
    db_session.flush()

    interaction = Interaction(
        client_id=client.id,
        channel=CommunicationChannel.WEB.value,
        direction=InteractionDirection.INCOMING.value,
        interaction_type=InteractionType.MESSAGE.value,
        intent_category=AIIntentCategory.APPOINTMENT_ASSISTANCE.value,
        message_reference="MSG-TEST-001",
        content="Hello, I need information about my next visit.",
    )
    db_session.add(interaction)
    db_session.flush()

    retrieved = db_session.get(Interaction, interaction.id)
    assert retrieved is not None
    assert retrieved.direction == InteractionDirection.INCOMING.value
    assert retrieved.intent_category == AIIntentCategory.APPOINTMENT_ASSISTANCE.value


def test_follow_up_task_and_escalation_with_staff_assignment(db_session):
    """Test FollowUpTask and Escalation with user assignment."""
    role = Role(name="staff_role_test", description="Staff role")
    db_session.add(role)
    db_session.flush()

    staff = User(
        role_id=role.id,
        email="assigned.staff@example.test",
        password_hash="hash",
        first_name="Staff",
        last_name="Member",
    )
    client = Client(
        external_reference="CLIENT-SYNTH-004",
        preferred_name="Demo Client 004",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE.value,
    )
    db_session.add_all([staff, client])
    db_session.flush()

    # Create FollowUpTask
    task = FollowUpTask(
        client_id=client.id,
        assigned_to=staff.id,
        reason="Missed routine appointment follow-up",
        priority=FollowUpPriority.NORMAL.value,
        status=FollowUpStatus.PENDING.value,
        due_at=datetime.now(timezone.utc) + timedelta(days=2),
    )
    # Create Escalation
    escalation = Escalation(
        client_id=client.id,
        assigned_to=staff.id,
        category=EscalationCategory.CLINICAL_CONCERN.value,
        priority=FollowUpPriority.HIGH.value,
        reason="Client reported medication side effect requiring human review",
        status=EscalationStatus.OPEN.value,
    )
    db_session.add_all([task, escalation])
    db_session.flush()

    # Verify task relationships
    retrieved_task = db_session.get(FollowUpTask, task.id)
    assert retrieved_task.assignee.email == "assigned.staff@example.test"
    assert retrieved_task.client.id == client.id

    # Verify escalation relationships
    retrieved_esc = db_session.get(Escalation, escalation.id)
    assert retrieved_esc.category == EscalationCategory.CLINICAL_CONCERN.value
    assert retrieved_esc.status == EscalationStatus.OPEN.value
    assert retrieved_esc.assignee.id == staff.id


def test_approved_information_model(db_session):
    """Test ApprovedInformation model for AI knowledge retrieval."""
    info = ApprovedInformation(
        title="Clinic Operating Hours",
        category=ApprovedInfoCategory.CLINIC_LOGISTICS.value,
        content="The clinic operates Monday to Friday from 8:00 AM to 4:00 PM.",
        version=1,
        is_active=True,
    )
    db_session.add(info)
    db_session.flush()

    retrieved = db_session.get(ApprovedInformation, info.id)
    assert retrieved is not None
    assert retrieved.title == "Clinic Operating Hours"
    assert retrieved.category == ApprovedInfoCategory.CLINIC_LOGISTICS.value
    assert retrieved.is_active is True


def test_audit_log_model(db_session):
    """Test AuditLog model with JSON metadata."""
    role = Role(name="audit_admin_role", description="Admin")
    db_session.add(role)
    db_session.flush()

    user = User(
        role_id=role.id,
        email="audit.user@example.test",
        password_hash="hash",
        first_name="Auditor",
        last_name="User",
    )
    db_session.add(user)
    db_session.flush()

    audit_entry = AuditLog(
        user_id=user.id,
        action="client_created",
        entity_type="client",
        entity_id=uuid.uuid4(),
        metadata_={"synthetic_batch": "demo_2026_09"},
    )
    db_session.add(audit_entry)
    db_session.flush()

    retrieved = db_session.get(AuditLog, audit_entry.id)
    assert retrieved is not None
    assert retrieved.action == "client_created"
    assert retrieved.user.email == "audit.user@example.test"
    assert retrieved.event_metadata == {"synthetic_batch": "demo_2026_09"}


def test_cascade_delete_client_cleans_child_records(db_session):
    """Verify that deleting a client cascades to appointments, tasks, and preferences."""
    client = Client(
        external_reference="CLIENT-CASCADE-TEST",
        preferred_name="Cascade Client",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE.value,
    )
    db_session.add(client)
    db_session.flush()

    appointment = Appointment(
        client_id=client.id,
        appointment_type="Lab Visit",
        scheduled_at=datetime.now(timezone.utc),
        status=AppointmentStatus.SCHEDULED.value,
    )
    pref = CommunicationPreference(
        client_id=client.id,
        channel=CommunicationChannel.SMS.value,
    )
    db_session.add_all([appointment, pref])
    db_session.flush()

    app_id = appointment.id
    pref_id = pref.id

    # Delete the client
    db_session.delete(client)
    db_session.flush()

    assert db_session.get(Appointment, app_id) is None
    assert db_session.get(CommunicationPreference, pref_id) is None
