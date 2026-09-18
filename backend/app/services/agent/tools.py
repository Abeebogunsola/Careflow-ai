"""
Controlled Tool Service for CareFlow AI.

Source of truth: docs/ai-agent-specification.md - Sections 10-18, 26, 27
and docs/safety-privacy.md - Section 24.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.client import Client
from app.models.appointment import Appointment
from app.models.approved_info import ApprovedInformation
from app.models.follow_up import FollowUpTask
from app.models.escalation import Escalation
from app.models.interaction import Interaction
from app.services.audit import record_audit


def get_client_profile(db: Session, client_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Retrieves permitted client information required for the current interaction.
    Enforces data minimization (docs/ai-agent-specification.md Section 10).
    Does NOT return clinical or unrestricted records.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None

    return {
        "id": str(client.id),
        "preferred_name": client.preferred_name or "Client",
        "preferred_language": client.preferred_language,
        "enrollment_status": client.enrollment_status,
        "is_active": client.is_active,
    }


def get_appointment(db: Session, client_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Retrieves verified upcoming or latest appointment information.
    The agent must not invent appointment dates or availability (Section 11).
    """
    now = datetime.now(timezone.utc)
    # Prefer scheduled appointments in future or present
    upcoming = (
        db.query(Appointment)
        .filter(
            Appointment.client_id == client_id,
            Appointment.status == "scheduled",
        )
        .order_by(Appointment.scheduled_at.asc())
        .first()
    )

    if not upcoming:
        # Check most recent past or modified appointment
        upcoming = (
            db.query(Appointment)
            .filter(Appointment.client_id == client_id)
            .order_by(Appointment.scheduled_at.desc())
            .first()
        )

    if not upcoming:
        return None

    return {
        "id": str(upcoming.id),
        "scheduled_at": upcoming.scheduled_at.isoformat(),
        "status": upcoming.status,
        "appointment_type": upcoming.appointment_type,
        "location_label": upcoming.location_label or "Main Program Clinic",
    }


def get_approved_information(
    db: Session,
    category: Optional[str] = None,
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves active approved program and logistical information (Section 17).
    """
    stmt = db.query(ApprovedInformation).filter(ApprovedInformation.is_active.is_(True))
    if category:
        stmt = stmt.filter(ApprovedInformation.category == category)
    if query:
        search_filter = f"%{query}%"
        stmt = stmt.filter(
            (ApprovedInformation.title.ilike(search_filter))
            | (ApprovedInformation.content.ilike(search_filter))
        )

    results = stmt.limit(5).all()
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "category": r.category,
            "content": r.content,
            "version": r.version,
        }
        for r in results
    ]


def create_followup(
    db: Session,
    client_id: uuid.UUID,
    reason: str,
    priority: str = "normal",
    due_at: Optional[datetime] = None,
) -> FollowUpTask:
    """
    Creates a follow-up task for human staff and records an audit log.
    """
    task = FollowUpTask(
        client_id=client_id,
        reason=reason,
        priority=priority,
        status="pending",
        due_at=due_at,
    )
    db.add(task)
    db.flush()

    record_audit(
        db=db,
        action="followup_created",
        entity_type="follow_up_task",
        entity_id=task.id,
        metadata={"priority": priority, "reason": reason},
    )
    return task


def create_escalation(
    db: Session,
    client_id: uuid.UUID,
    category: str,
    priority: str,
    reason: str,
) -> Escalation:
    """
    Creates a human-review escalation and records an audit log.
    """
    escalation = Escalation(
        client_id=client_id,
        category=category,
        priority=priority,
        reason=reason,
        status="open",
    )
    db.add(escalation)
    db.flush()

    record_audit(
        db=db,
        action="escalation_created",
        entity_type="escalation",
        entity_id=escalation.id,
        metadata={"category": category, "priority": priority, "reason": reason},
    )
    return escalation


def record_interaction(
    db: Session,
    client_id: uuid.UUID,
    channel: str,
    direction: str,
    interaction_type: str,
    intent_category: Optional[str] = None,
    content: Optional[str] = None,
    message_reference: Optional[str] = None,
) -> Interaction:
    """
    Records an interaction for auditability and support history.
    """
    interaction = Interaction(
        client_id=client_id,
        channel=channel,
        direction=direction,
        interaction_type=interaction_type,
        intent_category=intent_category,
        content=content,
        message_reference=message_reference,
    )
    db.add(interaction)
    db.flush()
    return interaction
