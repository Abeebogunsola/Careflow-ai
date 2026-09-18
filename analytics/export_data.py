"""
Analytics Data Extraction & Star Schema Export Utility for CareFlow AI (Phase 9).

Source of truth: docs/system-architecture.md - Section 17 & docs/database-design.md - Section 42.

Extracts de-identified operational data into analytical CSV datasets in `analytics/data/`:
- `dim_date.csv`: Calendar dimension.
- `dim_client.csv`: De-identified client dimension with non-reversible surrogate hashes.
- `fact_appointments.csv`: Appointment attendance, completion, and scheduling facts.
- `fact_interactions.csv`: Interaction volume, channel distribution, and intent facts.
- `fact_followups.csv`: Follow-up task progress and non-clinical barrier reports.
- `fact_escalations.csv`: Escalation categories and staff turnaround hours.
- `agg_program_summary.csv`: Pre-calculated executive KPI snapshot.
- `agg_barriers.csv`: Aggregate barrier category distributions.

Guarantees 100% data minimization: zero patient names, phone numbers, or free-text clinical data.
"""

import csv
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure backend root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db.session import SessionLocal
from app.models import (
    Client,
    Appointment,
    Interaction,
    FollowUpTask,
    Escalation,
    EnrollmentStatus,
    AppointmentStatus,
    FollowUpStatus,
    EscalationStatus,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "data"


def hash_id(val: any) -> str:
    """Creates a deterministic, non-reversible 12-character surrogate hash key."""
    if not val:
        return "ANON-00000000"
    return "ANON-" + hashlib.sha256(str(val).encode("utf-8")).hexdigest()[:8].upper()


def extract_analytics_datasets(output_directory: Path = OUTPUT_DIR, db_session=None) -> dict:
    """
    Extracts de-identified star schema tables and writes CSV files for Power BI ingestion.
    Returns a dictionary of extracted record counts.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    should_close = False
    if db_session is None:
        db = SessionLocal()
        should_close = True
    else:
        db = db_session

    counts = {}

    try:
        # 1. Extract Clients (De-Identified)
        clients = db.query(Client).all()
        client_rows = []
        for c in clients:
            client_rows.append({
                "client_key": hash_id(c.id),
                "enrollment_status": c.enrollment_status,
                "preferred_language": c.preferred_language,
                "is_active": 1 if c.is_active else 0,
                "enrolled_date": c.created_at.strftime("%Y-%m-%d") if c.created_at else "",
            })
        
        dim_client_path = output_directory / "dim_client.csv"
        with open(dim_client_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["client_key", "enrollment_status", "preferred_language", "is_active", "enrolled_date"])
            writer.writeheader()
            writer.writerows(client_rows)
        counts["dim_client"] = len(client_rows)

        # 2. Extract Appointments & Calendar Keys
        appts = db.query(Appointment).all()
        appt_rows = []
        dates_seen = set()

        for a in appts:
            dt_str = a.scheduled_at.strftime("%Y-%m-%d") if a.scheduled_at else ""
            if dt_str:
                dates_seen.add(a.scheduled_at.date())

            is_completed = 1 if a.status == "completed" else 0
            is_missed = 1 if a.status == "missed" else 0
            is_scheduled = 1 if a.status == "scheduled" else 0
            is_cancelled = 1 if a.status == "cancelled" else 0
            is_rescheduled = 1 if a.status == "rescheduled" else 0

            appt_rows.append({
                "appointment_key": hash_id(a.id),
                "client_key": hash_id(a.client_id),
                "date_key": dt_str,
                "appointment_type": a.appointment_type,
                "status": a.status,
                "location_label": a.location_label or "Main Clinic",
                "is_completed": is_completed,
                "is_missed": is_missed,
                "is_scheduled": is_scheduled,
                "is_cancelled": is_cancelled,
                "is_rescheduled": is_rescheduled,
                "scheduled_hour": a.scheduled_at.hour if a.scheduled_at else 9,
            })

        fact_appt_path = output_directory / "fact_appointments.csv"
        with open(fact_appt_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "appointment_key", "client_key", "date_key", "appointment_type",
                "status", "location_label", "is_completed", "is_missed",
                "is_scheduled", "is_cancelled", "is_rescheduled", "scheduled_hour"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(appt_rows)
        counts["fact_appointments"] = len(appt_rows)

        # 3. Extract Date Dimension
        date_rows = []
        for d in sorted(dates_seen):
            month = d.month
            quarter = f"Q{(month - 1) // 3 + 1}"
            date_rows.append({
                "date_key": d.strftime("%Y-%m-%d"),
                "year": d.year,
                "quarter": quarter,
                "month": month,
                "month_name": d.strftime("%B"),
                "year_month": d.strftime("%Y-%m"),
                "day": d.day,
                "day_of_week": d.strftime("%A"),
                "is_weekend": 1 if d.weekday() >= 5 else 0,
            })

        dim_date_path = output_directory / "dim_date.csv"
        with open(dim_date_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["date_key", "year", "quarter", "month", "month_name", "year_month", "day", "day_of_week", "is_weekend"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(date_rows)
        counts["dim_date"] = len(date_rows)

        # 4. Extract Interactions
        interactions = db.query(Interaction).all()
        inter_rows = []
        for i in interactions:
            dt_str = i.created_at.strftime("%Y-%m-%d") if i.created_at else ""
            inter_rows.append({
                "interaction_key": hash_id(i.id),
                "client_key": hash_id(i.client_id),
                "date_key": dt_str,
                "channel": i.channel,
                "direction": i.direction,
                "interaction_type": i.interaction_type,
                "intent_category": i.intent_category or "unclassified",
                "is_incoming": 1 if i.direction == "incoming" else 0,
                "is_outgoing": 1 if i.direction == "outgoing" else 0,
                "is_reminder": 1 if i.interaction_type == "appointment_reminder" else 0,
            })

        fact_inter_path = output_directory / "fact_interactions.csv"
        with open(fact_inter_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "interaction_key", "client_key", "date_key", "channel",
                "direction", "interaction_type", "intent_category",
                "is_incoming", "is_outgoing", "is_reminder"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(inter_rows)
        counts["fact_interactions"] = len(inter_rows)

        # 5. Extract Follow-Up Tasks & Barriers
        followups = db.query(FollowUpTask).all()
        fu_rows = []
        barrier_counts = {}

        for fu in followups:
            dt_str = fu.created_at.strftime("%Y-%m-%d") if fu.created_at else ""
            reason_lower = (fu.reason or "").lower()

            if "transport" in reason_lower:
                barrier = "transport"
            elif "schedule" in reason_lower or "work" in reason_lower:
                barrier = "schedule"
            elif "financial" in reason_lower or "money" in reason_lower or "fare" in reason_lower:
                barrier = "financial_or_logistical"
            elif "communicat" in reason_lower or "phone" in reason_lower:
                barrier = "communication"
            elif "clinic" in reason_lower or "access" in reason_lower:
                barrier = "clinic_access"
            elif "social" in reason_lower or "stigma" in reason_lower or "peer" in reason_lower:
                barrier = "social_support"
            else:
                barrier = "general_support"

            barrier_counts[barrier] = barrier_counts.get(barrier, 0) + 1

            is_pending = 1 if fu.status == "pending" else 0
            is_completed = 1 if fu.status == "completed" else 0

            fu_rows.append({
                "followup_key": hash_id(fu.id),
                "client_key": hash_id(fu.client_id),
                "date_key": dt_str,
                "priority": fu.priority,
                "status": fu.status,
                "barrier_category": barrier,
                "is_pending": is_pending,
                "is_completed": is_completed,
            })

        fact_fu_path = output_directory / "fact_followups.csv"
        with open(fact_fu_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["followup_key", "client_key", "date_key", "priority", "status", "barrier_category", "is_pending", "is_completed"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(fu_rows)
        counts["fact_followups"] = len(fu_rows)

        # 6. Extract Escalations
        escalations = db.query(Escalation).all()
        esc_rows = []
        for e in escalations:
            dt_str = e.created_at.strftime("%Y-%m-%d") if e.created_at else ""
            res_hours = 0.0
            if e.resolved_at and e.created_at and e.resolved_at >= e.created_at:
                res_hours = round((e.resolved_at - e.created_at).total_seconds() / 3600.0, 2)

            esc_rows.append({
                "escalation_key": hash_id(e.id),
                "client_key": hash_id(e.client_id),
                "date_key": dt_str,
                "escalation_category": e.category,
                "priority": e.priority,
                "status": e.status,
                "is_open": 1 if e.status == "open" else 0,
                "is_resolved": 1 if e.status == "resolved" else 0,
                "resolution_hours": res_hours,
            })

        fact_esc_path = output_directory / "fact_escalations.csv"
        with open(fact_esc_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["escalation_key", "client_key", "date_key", "escalation_category", "priority", "status", "is_open", "is_resolved", "resolution_hours"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(esc_rows)
        counts["fact_escalations"] = len(esc_rows)

        # 7. Pre-calculated Barrier Aggregate
        barrier_rows = [
            {"barrier_category": k, "report_count": v}
            for k, v in sorted(barrier_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        agg_barrier_path = output_directory / "agg_barriers.csv"
        with open(agg_barrier_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["barrier_category", "report_count"])
            writer.writeheader()
            writer.writerows(barrier_rows)
        counts["agg_barriers"] = len(barrier_rows)

        # 8. Pre-calculated Program Overview KPI Summary
        active_count = sum(1 for c in client_rows if c["is_active"] == 1)
        completed_count = sum(1 for a in appt_rows if a["is_completed"] == 1)
        missed_count = sum(1 for a in appt_rows if a["is_missed"] == 1)
        finalized = completed_count + missed_count
        adherence_rate = round((completed_count / finalized) * 100.0, 2) if finalized > 0 else 0.0

        summary_rows = [{
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_clients": len(client_rows),
            "active_clients": active_count,
            "total_appointments": len(appt_rows),
            "completed_appointments": completed_count,
            "missed_appointments": missed_count,
            "adherence_rate_pct": adherence_rate,
            "total_interactions": len(inter_rows),
            "total_followups": len(fu_rows),
            "total_escalations": len(esc_rows),
        }]
        agg_summary_path = output_directory / "agg_program_summary.csv"
        with open(agg_summary_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = list(summary_rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        counts["agg_program_summary"] = len(summary_rows)

        print("Analytics extraction completed successfully:")
        for name, count in counts.items():
            print(f"  - {name}.csv: {count} rows")

        return counts

    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    extract_analytics_datasets()
