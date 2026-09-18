"""
Analytics Endpoints for CareFlow AI.

Source of truth: docs/api.md - Section 50, docs/system-architecture.md - Section 17, and docs/workflows.md - Workflow 11.
Provides aggregate program-level metrics with zero personally identifiable information (PII).
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.escalation import Escalation
from app.models.follow_up import FollowUpTask
from app.models.interaction import Interaction
from app.models.enums import (
    AppointmentStatus,
    EnrollmentStatus,
    EscalationStatus,
    FollowUpStatus,
)
from app.schemas.analytics import AnalyticsOverviewRead, AnalyticsOverviewResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get aggregate program analytics",
    description="Returns aggregate counts across clients, appointments, follow-ups, escalations, and interactions with zero PII.",
)
def get_analytics_overview(db: Session = Depends(get_db)) -> AnalyticsOverviewResponse:
    """
    Computes program-level operational counts for dashboards, reports, and n8n summary workflows.
    Ensures absolute privacy by exposing zero individual or clinical details.
    """
    active_clients = db.scalar(
        select(func.count(Client.id)).where(Client.enrollment_status == EnrollmentStatus.ACTIVE)
    ) or 0

    appointments_scheduled = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.SCHEDULED)
    ) or 0

    appointments_completed = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.COMPLETED)
    ) or 0

    appointments_missed = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.MISSED)
    ) or 0

    followups_pending = db.scalar(
        select(func.count(FollowUpTask.id)).where(FollowUpTask.status == FollowUpStatus.PENDING)
    ) or 0

    followups_completed = db.scalar(
        select(func.count(FollowUpTask.id)).where(FollowUpTask.status == FollowUpStatus.COMPLETED)
    ) or 0

    escalations_open = db.scalar(
        select(func.count(Escalation.id)).where(Escalation.status == EscalationStatus.OPEN)
    ) or 0

    escalations_resolved = db.scalar(
        select(func.count(Escalation.id)).where(Escalation.status == EscalationStatus.RESOLVED)
    ) or 0

    interactions_count = db.scalar(
        select(func.count(Interaction.id))
    ) or 0

    data = AnalyticsOverviewRead(
        active_clients=active_clients,
        appointments_scheduled=appointments_scheduled,
        appointments_completed=appointments_completed,
        appointments_missed=appointments_missed,
        followups_pending=followups_pending,
        followups_completed=followups_completed,
        escalations_open=escalations_open,
        escalations_resolved=escalations_resolved,
        interactions_count=interactions_count,
    )

    return AnalyticsOverviewResponse(data=data)
