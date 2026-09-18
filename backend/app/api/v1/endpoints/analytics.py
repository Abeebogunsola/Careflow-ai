"""
Analytics Endpoints for CareFlow AI.

Source of truth: docs/api.md - Section 25, docs/system-architecture.md - Section 17, and docs/workflows.md - Workflow 11.
Provides aggregate program-level metrics with zero personally identifiable information (PII).
"""

from datetime import datetime
from typing import Dict, Optional
from fastapi import APIRouter, Depends, Query
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
    InteractionDirection,
)
from app.schemas.analytics import (
    AnalyticsOverviewRead,
    AnalyticsOverviewResponse,
    AppointmentAnalyticsRead,
    AppointmentAnalyticsResponse,
    EngagementAnalyticsRead,
    EngagementAnalyticsResponse,
    EscalationSummaryMetrics,
    FollowUpSummaryMetrics,
)

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


@router.get(
    "/appointments",
    response_model=AppointmentAnalyticsResponse,
    summary="Get appointment retention and adherence analytics",
    description="Returns detailed appointment volume, adherence rates, and visit type distributions with zero PII.",
)
def get_appointment_analytics(
    start_date: Optional[datetime] = Query(None, description="Filter appointments from this UTC timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter appointments up to this UTC timestamp"),
    appointment_type: Optional[str] = Query(None, description="Filter by specific appointment type"),
    db: Session = Depends(get_db),
) -> AppointmentAnalyticsResponse:
    """
    Computes appointment completion, missed, and cancellation rates for care retention tracking.
    """
    # Base query filters
    filters = []
    if start_date is not None:
        filters.append(Appointment.scheduled_at >= start_date)
    if end_date is not None:
        filters.append(Appointment.scheduled_at <= end_date)
    if appointment_type is not None:
        filters.append(Appointment.appointment_type == appointment_type)

    # Status counts
    scheduled_count = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.SCHEDULED, *filters)
    ) or 0

    completed_count = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.COMPLETED, *filters)
    ) or 0

    missed_count = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.MISSED, *filters)
    ) or 0

    cancelled_count = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.CANCELLED, *filters)
    ) or 0

    rescheduled_count = db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.RESCHEDULED, *filters)
    ) or 0

    total_appointments = (
        scheduled_count + completed_count + missed_count + cancelled_count + rescheduled_count
    )

    # Completion Rate = Completed / Finalized (Completed + Missed + Cancelled)
    finalized = completed_count + missed_count + cancelled_count
    completion_rate = round((completed_count / finalized) * 100.0, 2) if finalized > 0 else 0.0

    # Missed Rate = Missed / (Completed + Missed)
    attendance_denom = completed_count + missed_count
    missed_rate = round((missed_count / attendance_denom) * 100.0, 2) if attendance_denom > 0 else 0.0

    # Type breakdown
    type_query = select(
        Appointment.appointment_type,
        func.count(Appointment.id),
    ).where(*filters).group_by(Appointment.appointment_type)
    by_type = {row[0]: row[1] for row in db.execute(type_query).all()}

    data = AppointmentAnalyticsRead(
        total_appointments=total_appointments,
        scheduled_count=scheduled_count,
        completed_count=completed_count,
        missed_count=missed_count,
        cancelled_count=cancelled_count,
        rescheduled_count=rescheduled_count,
        completion_rate=completion_rate,
        missed_rate=missed_rate,
        by_type=by_type,
    )

    return AppointmentAnalyticsResponse(data=data)


@router.get(
    "/engagement",
    response_model=EngagementAnalyticsResponse,
    summary="Get engagement, communication, and barrier analytics",
    description="Returns interaction channel volumes, intent breakdowns, non-clinical barrier frequencies, and escalation turnaround with zero PII.",
)
def get_engagement_analytics(
    start_date: Optional[datetime] = Query(None, description="Filter events from this UTC timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter events up to this UTC timestamp"),
    db: Session = Depends(get_db),
) -> EngagementAnalyticsResponse:
    """
    Computes communication channel usage, intent categorization, barrier distribution,
    and escalation turnaround metrics for program managers and Power BI dashboards.
    """
    # 1. Interactions
    int_filters = []
    if start_date is not None:
        int_filters.append(Interaction.created_at >= start_date)
    if end_date is not None:
        int_filters.append(Interaction.created_at <= end_date)

    total_interactions = db.scalar(
        select(func.count(Interaction.id)).where(*int_filters)
    ) or 0

    incoming_count = db.scalar(
        select(func.count(Interaction.id)).where(
            Interaction.direction == InteractionDirection.INCOMING, *int_filters
        )
    ) or 0

    outgoing_count = db.scalar(
        select(func.count(Interaction.id)).where(
            Interaction.direction == InteractionDirection.OUTGOING, *int_filters
        )
    ) or 0

    channel_rows = db.execute(
        select(Interaction.channel, func.count(Interaction.id)).where(*int_filters).group_by(Interaction.channel)
    ).all()
    by_channel = {str(row[0]): row[1] for row in channel_rows}

    type_rows = db.execute(
        select(Interaction.interaction_type, func.count(Interaction.id)).where(*int_filters).group_by(Interaction.interaction_type)
    ).all()
    by_type = {str(row[0]): row[1] for row in type_rows}

    intent_rows = db.execute(
        select(Interaction.intent_category, func.count(Interaction.id))
        .where(Interaction.intent_category.is_not(None), *int_filters)
        .group_by(Interaction.intent_category)
    ).all()
    by_intent = {str(row[0]): row[1] for row in intent_rows if row[0]}

    # 2. Barrier Distribution
    # Identified barriers are logged into follow-up tasks and interaction notes
    known_barrier_categories = [
        "transport",
        "schedule",
        "financial_or_logistical",
        "communication",
        "clinic_access",
        "social_support",
        "other",
    ]
    barrier_breakdown: Dict[str, int] = {}
    for cat in known_barrier_categories:
        count = db.scalar(
            select(func.count(FollowUpTask.id)).where(
                FollowUpTask.reason.ilike(f"%{cat}%")
            )
        ) or 0
        if count > 0:
            barrier_breakdown[cat] = count

    # 3. Escalations
    esc_filters = []
    if start_date is not None:
        esc_filters.append(Escalation.created_at >= start_date)
    if end_date is not None:
        esc_filters.append(Escalation.created_at <= end_date)

    total_escalations = db.scalar(
        select(func.count(Escalation.id)).where(*esc_filters)
    ) or 0

    open_escalations = db.scalar(
        select(func.count(Escalation.id)).where(Escalation.status == EscalationStatus.OPEN, *esc_filters)
    ) or 0

    resolved_escalations_count = db.scalar(
        select(func.count(Escalation.id)).where(Escalation.status == EscalationStatus.RESOLVED, *esc_filters)
    ) or 0

    esc_cat_rows = db.execute(
        select(Escalation.category, func.count(Escalation.id)).where(*esc_filters).group_by(Escalation.category)
    ).all()
    esc_by_category = {str(row[0]): row[1] for row in esc_cat_rows}

    # Turnaround time in hours for resolved escalations
    resolved_rows = db.execute(
        select(Escalation.created_at, Escalation.resolved_at).where(
            Escalation.status == EscalationStatus.RESOLVED,
            Escalation.resolved_at.is_not(None),
            *esc_filters,
        )
    ).all()
    if resolved_rows:
        durations = [
            (row[1] - row[0]).total_seconds() / 3600.0
            for row in resolved_rows
            if row[1] and row[0] and row[1] >= row[0]
        ]
        avg_resolution_hours = round(sum(durations) / len(durations), 2) if durations else 0.0
    else:
        avg_resolution_hours = 0.0

    escalation_metrics = EscalationSummaryMetrics(
        total_escalations=total_escalations,
        open_count=open_escalations,
        resolved_count=resolved_escalations_count,
        by_category=esc_by_category,
        avg_resolution_hours=avg_resolution_hours,
    )

    # 4. Follow-Ups
    fu_filters = []
    if start_date is not None:
        fu_filters.append(FollowUpTask.created_at >= start_date)
    if end_date is not None:
        fu_filters.append(FollowUpTask.created_at <= end_date)

    total_followups = db.scalar(
        select(func.count(FollowUpTask.id)).where(*fu_filters)
    ) or 0

    pending_followups = db.scalar(
        select(func.count(FollowUpTask.id)).where(FollowUpTask.status == FollowUpStatus.PENDING, *fu_filters)
    ) or 0

    completed_followups = db.scalar(
        select(func.count(FollowUpTask.id)).where(FollowUpTask.status == FollowUpStatus.COMPLETED, *fu_filters)
    ) or 0

    fu_completion_rate = (
        round((completed_followups / total_followups) * 100.0, 2) if total_followups > 0 else 0.0
    )

    followup_metrics = FollowUpSummaryMetrics(
        total_followups=total_followups,
        pending_count=pending_followups,
        completed_count=completed_followups,
        completion_rate=fu_completion_rate,
    )

    data = EngagementAnalyticsRead(
        total_interactions=total_interactions,
        incoming_count=incoming_count,
        outgoing_count=outgoing_count,
        by_channel=by_channel,
        by_type=by_type,
        by_intent=by_intent,
        barrier_breakdown=barrier_breakdown,
        escalation_metrics=escalation_metrics,
        followup_metrics=followup_metrics,
    )

    return EngagementAnalyticsResponse(data=data)
