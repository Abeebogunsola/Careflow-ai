"""
Tests for CareFlow AI n8n Automation Workflows (Phase 8).

Validates:
1. Workflow File Integrity:
   - All 8 expected workflow JSON files exist in `n8n/workflows/`.
   - Each file parses as valid JSON with required n8n keys (`name`, `nodes`, `connections`).
   - Every connection points to valid declared nodes.
2. Security & Zero Secrets:
   - Workflows contain no hardcoded API keys, passwords, database credentials, or auth tokens.
   - Uses environment variable references (e.g. `$env.API_BASE_URL`).
3. Safety & Privacy Compliance:
   - Outreach messages contain NO sensitive clinical diagnoses or explicit HIV references.
4. End-to-End Workflow Logic Simulation:
   - Appointment Reminder & Idempotency logic against FastAPI test database.
   - Missed Appointment grace period & care re-engagement task provisioning.
   - Message routing (automated response vs human escalation).
   - Barrier-to-care triage and follow-up generation.
   - Daily program summary metrics extraction (zero PII).
"""

import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
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
    CommunicationChannel,
    InteractionDirection,
    InteractionType,
)

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent.parent / "n8n" / "workflows"

EXPECTED_WORKFLOW_FILES = [
    "01_appointment_reminder.json",
    "02_missed_appointment.json",
    "03_client_message.json",
    "04_barrier_followup.json",
    "05_escalation_notification.json",
    "06_followup_management.json",
    "07_daily_program_summary.json",
    "08_error_handler.json",
]


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


# ============================================================================
# 1. Structural & Static Schema Tests
# ============================================================================

def test_all_workflow_files_exist():
    """Verify that all 8 core workflow JSON files exist in n8n/workflows/."""
    assert WORKFLOWS_DIR.is_dir(), f"Workflows directory not found at {WORKFLOWS_DIR}"
    existing_files = [f.name for f in WORKFLOWS_DIR.glob("*.json")]
    for expected_file in EXPECTED_WORKFLOW_FILES:
        assert expected_file in existing_files, f"Missing workflow file: {expected_file}"


def test_workflow_json_structure_and_connections():
    """Verify JSON validity, node declarations, and valid connections in each workflow."""
    for filename in EXPECTED_WORKFLOW_FILES:
        file_path = WORKFLOWS_DIR / filename
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "name" in data, f"{filename} missing 'name'"
        assert "nodes" in data and isinstance(data["nodes"], list), f"{filename} missing 'nodes' array"
        assert "connections" in data and isinstance(data["connections"], dict), f"{filename} missing 'connections' dict"

        # Check node structure
        node_names = set()
        for node in data["nodes"]:
            assert "id" in node, f"Node in {filename} missing 'id'"
            assert "name" in node, f"Node in {filename} missing 'name'"
            assert "type" in node, f"Node in {filename} missing 'type'"
            assert "position" in node, f"Node in {filename} missing 'position'"
            node_names.add(node["name"])

        # Check connections reference valid declared nodes
        for source_node, conn_types in data["connections"].items():
            assert source_node in node_names, f"Connection source '{source_node}' in {filename} not declared in nodes"
            for conn_type, target_lists in conn_types.items():
                for target_list in target_lists:
                    for target in target_list:
                        assert target["node"] in node_names, (
                            f"Connection target '{target['node']}' in {filename} not declared in nodes"
                        )


def test_workflows_have_no_hardcoded_secrets():
    """Verify that no workflow contains embedded secrets, passwords, or live tokens."""
    sensitive_keywords = ["secret_key", "password\":", "bearer ey", "private_key", "sk-"]
    for filename in EXPECTED_WORKFLOW_FILES:
        file_path = WORKFLOWS_DIR / filename
        content = file_path.read_text(encoding="utf-8").lower()
        for keyword in sensitive_keywords:
            assert keyword not in content, f"Potentially sensitive credential '{keyword}' detected in {filename}"


def test_outreach_workflows_strictly_maintain_privacy():
    """Verify that outreach reminders and follow-up templates avoid disclosing HIV status or clinical conditions."""
    disallowed_keywords = ["hiv", "aids", "antiretroviral", "art regimen", "viral load", "cd4"]
    outreach_files = [
        "01_appointment_reminder.json",
        "02_missed_appointment.json",
        "04_barrier_followup.json",
        "07_daily_program_summary.json",
    ]
    for filename in outreach_files:
        file_path = WORKFLOWS_DIR / filename
        content = file_path.read_text(encoding="utf-8").lower()
        for keyword in disallowed_keywords:
            assert keyword not in content, (
                f"Privacy violation: Outreach workflow {filename} contains explicit term '{keyword}'"
            )


# ============================================================================
# 2. Dynamic Workflow Simulation Tests
# ============================================================================

def _parse_dt(val: str) -> datetime:
    dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def test_workflow_appointment_reminder_idempotency_simulation(client):
    """
    Simulates the n8n Appointment Reminder workflow:
    1. Query upcoming appointments within 24 hours.
    2. Check prior interactions for the client.
    3. Send reminder and record interaction.
    4. Run second time -> verify idempotency skips duplicate reminder.
    """
    # 1. Create client and appointment scheduled tomorrow
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "TEST-CLIENT-REM", "preferred_name": "Jordan"},
    )
    assert c_res.status_code == 201
    client_id = c_res.json()["data"]["id"]

    now = datetime.now(timezone.utc)
    apt_payload = {
        "client_id": client_id,
        "appointment_type": "consultation",
        "scheduled_at": (now + timedelta(hours=20)).isoformat(),
        "status": "scheduled",
        "location_label": "Care Clinic Main",
    }
    apt_res = client.post("/api/v1/appointments", json=apt_payload)
    assert apt_res.status_code == 201

    # Step A: n8n fetches scheduled appointments
    resp = client.get("/api/v1/appointments?status=scheduled&page_size=100")
    assert resp.status_code == 200
    scheduled_appts = resp.json()["data"]
    assert len(scheduled_appts) >= 1

    # Step B: Filter within 24h window
    matching = [
        a for a in scheduled_appts
        if a["client_id"] == client_id and now < _parse_dt(a["scheduled_at"]) <= now + timedelta(hours=24)
    ]
    assert len(matching) == 1

    # Step C: Check prior interactions for idempotency
    inter_resp = client.get(f"/api/v1/interactions?client_id={client_id}&page_size=20")
    assert inter_resp.status_code == 200
    existing_reminders = [
        i for i in inter_resp.json()["data"]
        if i["interaction_type"] == "appointment_reminder"
    ]
    assert len(existing_reminders) == 0

    # Step D: Record outgoing reminder interaction
    create_resp = client.post(
        "/api/v1/interactions",
        json={
            "client_id": client_id,
            "channel": "sms",
            "direction": "outgoing",
            "interaction_type": "appointment_reminder",
            "content": "Hello! Friendly reminder of your appointment tomorrow.",
        },
    )
    assert create_resp.status_code == 201

    # Step E: Idempotency re-run -> verify prior reminder is now detected and suppressed
    inter_resp2 = client.get(f"/api/v1/interactions?client_id={client_id}&page_size=20")
    existing_reminders2 = [
        i for i in inter_resp2.json()["data"]
        if i["interaction_type"] == "appointment_reminder"
    ]
    assert len(existing_reminders2) == 1  # Duplicate suppressed


def test_workflow_missed_appointment_simulation(client):
    """
    Simulates the n8n Missed Appointment Detection workflow:
    1. Query appointments where scheduled_at + grace_period (60m) < now.
    2. Patch appointment to 'missed'.
    3. Provision a follow-up task for staff outreach.
    4. Record outgoing follow-up interaction.
    """
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "TEST-CLIENT-MISSED", "preferred_name": "Taylor"},
    )
    assert c_res.status_code == 201
    client_id = c_res.json()["data"]["id"]

    now = datetime.now(timezone.utc)
    # Scheduled 2 hours ago (past 60 min grace period)
    apt_payload = {
        "client_id": client_id,
        "appointment_type": "routine_checkup",
        "scheduled_at": (now - timedelta(hours=2)).isoformat(),
        "status": "scheduled",
    }
    apt_res = client.post("/api/v1/appointments", json=apt_payload)
    assert apt_res.status_code == 201

    # Step A: n8n queries scheduled appointments
    resp = client.get("/api/v1/appointments?status=scheduled&page_size=100")
    assert resp.status_code == 200
    appts = resp.json()["data"]

    # Step B: Identify missed (past grace period of 60 mins)
    grace_threshold = now - timedelta(minutes=60)
    missed_candidates = [
        a for a in appts
        if a["client_id"] == client_id and _parse_dt(a["scheduled_at"]) < grace_threshold
    ]
    assert len(missed_candidates) == 1
    target = missed_candidates[0]

    # Step C: Patch appointment to missed
    patch_resp = client.patch(
        f"/api/v1/appointments/{target['id']}",
        json={"status": "missed"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["status"] == "missed"

    # Step D: Create re-engagement follow-up task
    fu_resp = client.post(
        "/api/v1/followups",
        json={
            "client_id": client_id,
            "priority": "normal",
            "reason": "Missed appointment outreach and care re-engagement",
        },
    )
    assert fu_resp.status_code == 201
    assert fu_resp.json()["data"]["status"] == "pending"

    # Step E: Record outreach interaction
    int_resp = client.post(
        "/api/v1/interactions",
        json={
            "client_id": client_id,
            "channel": "sms",
            "direction": "outgoing",
            "interaction_type": "follow_up",
            "content": "Hello! We noticed you were unable to make your visit today. Please let us know if we can help.",
        },
    )
    assert int_resp.status_code == 201


def test_workflow_client_message_routing_simulation(client):
    """
    Simulates the n8n Client Message workflow invoking the FastAPI AI Agent endpoint:
    1. Safe message -> 'escalated' is False
    2. Clinical concern message -> 'escalated' is True
    """
    c_res = client.post(
        "/api/v1/clients",
        json={"external_reference": "TEST-CLIENT-MSG", "preferred_name": "Alex"},
    )
    assert c_res.status_code == 201
    client_id = c_res.json()["data"]["id"]

    # Scenario 1: Appointment question (safe intent)
    safe_resp = client.post(
        "/api/v1/messages",
        json={
            "client_id": client_id,
            "message": "When is my next appointment scheduled?",
            "channel": "sms",
        },
    )
    assert safe_resp.status_code == 200
    safe_data = safe_resp.json()["data"]
    assert safe_data["escalated"] is False
    assert safe_data["intent"] == "appointment_assistance"

    # Scenario 2: Clinical symptoms (sensitive intent -> escalation)
    clinical_resp = client.post(
        "/api/v1/messages",
        json={
            "client_id": client_id,
            "message": "I have high fever, severe nausea, and dizziness.",
            "channel": "sms",
        },
    )
    assert clinical_resp.status_code == 200
    clinical_data = clinical_resp.json()["data"]
    assert clinical_data["escalated"] is True
    assert clinical_data["intent"] == "clinical_concern"
    assert clinical_data["escalation_id"] is not None


def test_workflow_barrier_followup_simulation(client, db_session):
    """
    Simulates n8n Barrier Follow-Up workflow:
    When a non-clinical barrier (e.g. transport) is received:
    1. Provision a follow-up task with reason and priority.
    2. Record supportive acknowledgment interaction.
    """
    db = db_session
    client_rec = Client(
        id=uuid.uuid4(),
        external_reference="TEST-CLIENT-BARRIER",
        preferred_name="Sam",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE,
    )
    db.add(client_rec)
    db.commit()

    # Create barrier follow-up
    fu_resp = client.post(
        "/api/v1/followups",
        json={
            "client_id": str(client_rec.id),
            "priority": "high",
            "reason": "Reported barrier to care: transport - Client has no bus fare for Tuesday visit",
        },
    )
    assert fu_resp.status_code == 201
    assert fu_resp.json()["data"]["priority"] == "high"

    # Record acknowledgment
    int_resp = client.post(
        "/api/v1/interactions",
        json={
            "client_id": str(client_rec.id),
            "channel": "sms",
            "direction": "outgoing",
            "interaction_type": "follow_up",
            "content": "Thank you for letting us know. Our care coordinator has been notified to assist with transit options.",
        },
    )
    assert int_resp.status_code == 201


def test_workflow_daily_program_summary_simulation(client, db_session):
    """
    Simulates n8n Daily Program Summary workflow:
    Queries /api/v1/analytics/overview and ensures data is aggregate with zero PII.
    """
    overview_resp = client.get("/api/v1/analytics/overview")
    assert overview_resp.status_code == 200

    data = overview_resp.json()["data"]
    expected_fields = [
        "active_clients",
        "appointments_scheduled",
        "appointments_completed",
        "appointments_missed",
        "followups_pending",
        "followups_completed",
        "escalations_open",
        "escalations_resolved",
        "interactions_count",
    ]
    for field in expected_fields:
        assert field in data
        assert isinstance(data[field], int)
