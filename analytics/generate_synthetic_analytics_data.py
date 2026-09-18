"""
Synthetic Analytics Demonstration Data Generator for CareFlow AI (Phase 9).

Generates longitudinal synthetic program data spanning 90-180 days:
- ~100 synthetic clients with varied enrollment dates and language preferences.
- Realistic appointment schedules, attendance patterns, and care retention curves.
- Multi-channel interactions (SMS, WhatsApp, Web) demonstrating outreach and automated reminders.
- Realistic non-clinical barriers (transportation, schedule conflicts, financial obstacles).
- Human review escalations with realistic staff turnaround times.

Strictly synthetic data. Zero real patient information or PII.
"""

import os
import sys
import uuid
import random
from datetime import datetime, timezone, timedelta

# Ensure backend root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db.session import SessionLocal
from app.models import (
    Client,
    CommunicationPreference,
    Appointment,
    Interaction,
    FollowUpTask,
    Escalation,
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
)


FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Casey", "Riley", "Avery",
    "Quinn", "Skyler", "Dakota", "Reese", "Rowan", "Hayden", "Logan", "Kendall"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson"
]

APPOINTMENT_TYPES = ["clinical_review", "lab_visit", "refill", "counseling"]
LOCATIONS = ["Main Clinic Suite A", "Community Health Center", "Annex Clinic Room 4", "East Wing Outpatient"]
BARRIERS = [
    ("transport", "Client reported lack of bus fare / transit passes for clinic visit"),
    ("schedule", "Client has work shift conflict during clinic hours"),
    ("financial_or_logistical", "Client reported financial obstacle for co-pay or transport"),
    ("communication", "Phone service was temporarily disconnected"),
    ("clinic_access", "Client arrived after clinic check-in hours closed"),
    ("social_support", "Client expressed feeling overwhelmed and requested peer support"),
]


def seed_synthetic_analytics_data(num_clients: int = 100, days_history: int = 120):
    """Populates the database with realistic longitudinal synthetic analytics data."""
    db = SessionLocal()
    try:
        print(f"Generating synthetic analytics dataset: {num_clients} clients across {days_history} days...")
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days_history)

        created_clients = []

        # 1. Generate Synthetic Clients & Preferences
        for i in range(1, num_clients + 1):
            enrolled_at = start_date + timedelta(days=random.randint(0, days_history - 10))
            is_active = random.random() > 0.08  # 92% active retention
            pref_lang = random.choice(["en", "en", "en", "es", "fr"])
            pref_name = f"{random.choice(FIRST_NAMES)}_{i:03d}"

            client = Client(
                id=uuid.uuid4(),
                external_reference=f"SYNTH-DEMO-{i:04d}",
                preferred_name=pref_name,
                preferred_language=pref_lang,
                enrollment_status=EnrollmentStatus.ACTIVE if is_active else EnrollmentStatus.INACTIVE,
                is_active=is_active,
                created_at=enrolled_at,
            )
            db.add(client)
            created_clients.append(client)

            # Communication Preference
            channel = random.choice([
                CommunicationChannel.SMS,
                CommunicationChannel.SMS,
                CommunicationChannel.WHATSAPP,
                CommunicationChannel.WEB,
            ])
            pref = CommunicationPreference(
                id=uuid.uuid4(),
                client_id=client.id,
                channel=channel.value if hasattr(channel, "value") else str(channel),
                is_enabled=True,
            )
            db.add(pref)

        db.commit()

        # 2. Generate Appointments & Attendance Outcomes
        total_appointments = 0
        total_interactions = 0
        total_followups = 0
        total_escalations = 0

        for client in created_clients:
            num_appts = random.randint(2, 6)
            for j in range(num_appts):
                # Distribute appointments across time
                offset_days = random.randint(-days_history + 10, 30)
                appt_time = now + timedelta(days=offset_days, hours=random.randint(8, 16))

                # Determine status based on whether date is in past or future
                if appt_time > now:
                    status = AppointmentStatus.SCHEDULED
                else:
                    # Past appointment outcomes: 75% completed, 15% missed, 6% rescheduled, 4% cancelled
                    roll = random.random()
                    if roll < 0.75:
                        status = AppointmentStatus.COMPLETED
                    elif roll < 0.90:
                        status = AppointmentStatus.MISSED
                    elif roll < 0.96:
                        status = AppointmentStatus.RESCHEDULED
                    else:
                        status = AppointmentStatus.CANCELLED

                appt = Appointment(
                    id=uuid.uuid4(),
                    client_id=client.id,
                    appointment_type=random.choice(APPOINTMENT_TYPES),
                    scheduled_at=appt_time,
                    status=status,
                    location_label=random.choice(LOCATIONS),
                    created_at=appt_time - timedelta(days=random.randint(7, 21)),
                )
                db.add(appt)
                total_appointments += 1

                # Automated reminder interaction (if scheduled or completed)
                if status in [AppointmentStatus.COMPLETED, AppointmentStatus.SCHEDULED, AppointmentStatus.MISSED]:
                    reminder = Interaction(
                        id=uuid.uuid4(),
                        client_id=client.id,
                        channel=CommunicationChannel.SMS,
                        direction=InteractionDirection.OUTGOING,
                        interaction_type=InteractionType.APPOINTMENT_REMINDER,
                        content=f"Reminder: You have a scheduled clinic visit on {appt_time.strftime('%b %d')}.",
                        created_at=appt_time - timedelta(days=1),
                    )
                    db.add(reminder)
                    total_interactions += 1

                # If missed, generate follow-up task and outreach
                if status == AppointmentStatus.MISSED:
                    barrier_info = random.choice(BARRIERS)
                    fu = FollowUpTask(
                        id=uuid.uuid4(),
                        client_id=client.id,
                        priority=FollowUpPriority.HIGH if barrier_info[0] == "transport" else FollowUpPriority.NORMAL,
                        status=FollowUpStatus.COMPLETED if random.random() > 0.3 else FollowUpStatus.PENDING,
                        reason=f"Missed appointment on {appt_time.strftime('%b %d')}. Reported barrier: {barrier_info[0]} - {barrier_info[1]}",
                        created_at=appt_time + timedelta(hours=2),
                        due_at=appt_time + timedelta(days=2),
                        completed_at=appt_time + timedelta(days=1, hours=4) if random.random() > 0.3 else None,
                    )
                    db.add(fu)
                    total_followups += 1

                    outreach = Interaction(
                        id=uuid.uuid4(),
                        client_id=client.id,
                        channel=CommunicationChannel.SMS,
                        direction=InteractionDirection.OUTGOING,
                        interaction_type=InteractionType.FOLLOW_UP,
                        content="We noticed you missed your visit today. Please let us know if we can help with rescheduling.",
                        created_at=appt_time + timedelta(hours=3),
                    )
                    db.add(outreach)
                    total_interactions += 1

        # 3. Generate Inbound Messages & Intent Classifications
        for client in created_clients[:45]:
            msg_time = now - timedelta(days=random.randint(1, 90))
            inbound = Interaction(
                id=uuid.uuid4(),
                client_id=client.id,
                channel=CommunicationChannel.SMS,
                direction=InteractionDirection.INCOMING,
                interaction_type=InteractionType.MESSAGE,
                intent_category=random.choice([
                    AIIntentCategory.APPOINTMENT_ASSISTANCE,
                    AIIntentCategory.RESCHEDULING,
                    AIIntentCategory.GENERAL_SUPPORT,
                    AIIntentCategory.BARRIER_TO_CARE,
                ]),
                content="Can you check when my next lab appointment is?",
                created_at=msg_time,
            )
            reply = Interaction(
                id=uuid.uuid4(),
                client_id=client.id,
                channel=CommunicationChannel.SMS,
                direction=InteractionDirection.OUTGOING,
                interaction_type=InteractionType.AI_RESPONSE,
                intent_category=inbound.intent_category,
                content="Your next appointment is confirmed on your schedule.",
                created_at=msg_time + timedelta(minutes=1),
            )
            db.add_all([inbound, reply])
            total_interactions += 2

        # 4. Generate Clinical & Human Review Escalations
        for client in created_clients[:18]:
            esc_created = now - timedelta(days=random.randint(2, 60))
            is_resolved = random.random() > 0.25
            resolved_hours = random.uniform(1.5, 12.0)
            esc_cat = random.choice([
                EscalationCategory.CLINICAL_CONCERN,
                EscalationCategory.MEDICATION_CONCERN,
                EscalationCategory.HUMAN_REQUEST,
            ])
            esc = Escalation(
                id=uuid.uuid4(),
                client_id=client.id,
                category=esc_cat,
                priority=FollowUpPriority.HIGH if esc_cat != EscalationCategory.HUMAN_REQUEST else FollowUpPriority.NORMAL,
                reason=f"Client expressed inquiry regarding {esc_cat.value}. Routed for nurse review.",
                status=EscalationStatus.RESOLVED if is_resolved else EscalationStatus.OPEN,
                created_at=esc_created,
                resolved_at=esc_created + timedelta(hours=resolved_hours) if is_resolved else None,
            )
            db.add(esc)
            total_escalations += 1

        db.commit()
        print(f"Synthetic dataset created successfully:")
        print(f"  - Enrolled Clients: {num_clients}")
        print(f"  - Appointments: {total_appointments}")
        print(f"  - Interactions: {total_interactions}")
        print(f"  - Follow-up Tasks: {total_followups}")
        print(f"  - Escalations: {total_escalations}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding synthetic analytics data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_synthetic_analytics_data()
