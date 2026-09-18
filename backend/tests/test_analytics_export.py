"""
Unit and Integration Tests for Analytics Data Export & Star Schema Extraction (Phase 9).

Validates:
- Successful generation of all dimensional and fact CSV datasets.
- Expected column schemas and non-empty rows when data exists.
- Strict Zero-PII adherence: no client names, phone numbers, or free-text narrative data in any CSV.
- Deterministic surrogate hash key formatting (ANON-xxxxxxxx).
"""

import csv
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

# Ensure analytics directory and backend root are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.models import (
    Client,
    Appointment,
    Interaction,
    FollowUpTask,
    Escalation,
    EnrollmentStatus,
    AppointmentStatus,
)
from analytics.export_data import extract_analytics_datasets, hash_id


EXPECTED_FILES = [
    "dim_client.csv",
    "dim_date.csv",
    "fact_appointments.csv",
    "fact_interactions.csv",
    "fact_followups.csv",
    "fact_escalations.csv",
    "agg_barriers.csv",
    "agg_program_summary.csv",
]


def test_hash_id_deterministic_and_format():
    """Verify hash_id creates non-reversible ANON-xxxxxxxx format keys deterministically."""
    h1 = hash_id("client-12345")
    h2 = hash_id("client-12345")
    h3 = hash_id("client-67890")

    assert h1 == h2
    assert h1 != h3
    assert h1.startswith("ANON-")
    assert len(h1) == 13  # "ANON-" + 8 hex chars


def test_extract_empty_database(tmp_path, db_session):
    """Verify extraction generates all CSV files with headers even on an empty database."""
    counts = extract_analytics_datasets(output_directory=tmp_path, db_session=db_session)

    for filename in EXPECTED_FILES:
        filepath = tmp_path / filename
        assert filepath.exists(), f"Missing exported CSV: {filename}"
        assert filepath.stat().st_size > 0, f"File {filename} is completely empty (no headers)"

    assert counts["dim_client"] == 0
    assert counts["fact_appointments"] == 0
    assert counts["fact_interactions"] == 0
    assert counts["fact_followups"] == 0
    assert counts["fact_escalations"] == 0


def test_extract_populated_database_schemas_and_counts(tmp_path, db_session):
    """Verify extracted CSV files contain correct records and column schemas."""
    # 1. Seed test data
    now = datetime.now(timezone.utc)
    client = Client(
        preferred_name="Jane",
        external_reference="EXT-REF-12345",
        preferred_language="en",
        enrollment_status=EnrollmentStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(client)
    db_session.flush()

    appt = Appointment(
        client_id=client.id,
        scheduled_at=now + timedelta(days=2),
        appointment_type="viral_load",
        status=AppointmentStatus.COMPLETED,
        location_label="Clinic Site Alpha",
    )
    db_session.add(appt)

    interaction = Interaction(
        client_id=client.id,
        channel="sms",
        direction="incoming",
        interaction_type="client_query",
        intent_category="appointment_inquiry",
    )
    db_session.add(interaction)

    followup = FollowUpTask(
        client_id=client.id,
        reason="Client reported transport fare hardship to reach clinic",
        priority="medium",
        status="completed",
    )
    db_session.add(followup)

    escalation = Escalation(
        client_id=client.id,
        category="clinical_concern",
        reason="Client reports severe symptoms",
        priority="high",
        status="resolved",
        resolved_at=now + timedelta(hours=2),
    )
    db_session.add(escalation)
    db_session.flush()

    # 2. Run extraction
    counts = extract_analytics_datasets(output_directory=tmp_path, db_session=db_session)

    assert counts["dim_client"] == 1
    assert counts["fact_appointments"] == 1
    assert counts["fact_interactions"] == 1
    assert counts["fact_followups"] == 1
    assert counts["fact_escalations"] == 1
    assert counts["dim_date"] >= 1

    # 3. Verify dim_client.csv columns
    with open(tmp_path / "dim_client.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert "client_key" in rows[0]
        assert rows[0]["client_key"].startswith("ANON-")
        assert rows[0]["enrollment_status"] == "active"
        assert rows[0]["preferred_language"] == "en"

    # 4. Verify fact_appointments.csv columns
    with open(tmp_path / "fact_appointments.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["appointment_type"] == "viral_load"
        assert rows[0]["status"] == "completed"
        assert rows[0]["is_completed"] == "1"
        assert rows[0]["location_label"] == "Clinic Site Alpha"

    # 5. Verify fact_followups.csv & barrier categorization
    with open(tmp_path / "fact_followups.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["barrier_category"] == "transport"
        assert rows[0]["is_completed"] == "1"

    # 6. Verify fact_escalations.csv & resolution turnaround
    with open(tmp_path / "fact_escalations.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["escalation_category"] == "clinical_concern"
        assert rows[0]["is_resolved"] == "1"
        assert float(rows[0]["resolution_hours"]) > 0


def test_extract_strict_zero_pii(tmp_path, db_session):
    """
    Exhaustively scans all exported CSV files to ensure that NO client PII
    (name, phone number, clinical narrative note) is ever exported.
    """
    secret_preferred_name = "SuperSecretAlice"
    secret_external_ref = "EXT-REF-CONFIDENTIAL-9999"
    secret_clinical_note = "Confidential clinical diagnosis narrative details"

    client = Client(
        preferred_name=secret_preferred_name,
        external_reference=secret_external_ref,
        preferred_language="fr",
        enrollment_status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(client)
    db_session.flush()

    fu = FollowUpTask(
        client_id=client.id,
        reason=f"Transport issue: {secret_clinical_note}",
        priority="medium",
        status="pending",
    )
    db_session.add(fu)
    db_session.flush()

    # Extract
    extract_analytics_datasets(output_directory=tmp_path, db_session=db_session)

    # Scan every exported CSV file line by line
    for filename in EXPECTED_FILES:
        filepath = tmp_path / filename
        content = filepath.read_text(encoding="utf-8")

        assert secret_preferred_name not in content, f"PII Leak: Found name in {filename}"
        assert secret_external_ref not in content, f"PII Leak: Found external reference in {filename}"
        assert secret_clinical_note not in content, f"Clinical Note Leak: Found free-text in {filename}"
