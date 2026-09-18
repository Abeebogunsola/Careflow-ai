"""
Analytics Schemas for CareFlow AI.

Source of truth: docs/api.md - Section 25, docs/workflows.md - Workflow 11, and docs/system-architecture.md - Section 17.
Provides aggregate program-level metrics with zero personally identifiable information (PII).
"""

from typing import Dict
from pydantic import BaseModel, Field
from app.schemas.common import DataResponse


class AnalyticsOverviewRead(BaseModel):
    """
    Aggregate program-level operational metrics.
    Exposes zero personally identifiable or sensitive individual health data.
    """
    active_clients: int = Field(..., ge=0, description="Total active enrolled clients")
    appointments_scheduled: int = Field(..., ge=0, description="Total scheduled upcoming appointments")
    appointments_completed: int = Field(..., ge=0, description="Total completed appointments")
    appointments_missed: int = Field(..., ge=0, description="Total missed appointments")
    followups_pending: int = Field(..., ge=0, description="Total pending follow-up tasks")
    followups_completed: int = Field(..., ge=0, description="Total completed follow-up tasks")
    escalations_open: int = Field(..., ge=0, description="Total open human review escalations")
    escalations_resolved: int = Field(..., ge=0, description="Total resolved escalations")
    interactions_count: int = Field(..., ge=0, description="Total recorded communication interactions")


class AnalyticsOverviewResponse(DataResponse[AnalyticsOverviewRead]):
    """Standard envelope for program metrics overview."""
    pass


class AppointmentAnalyticsRead(BaseModel):
    """
    Detailed appointment adherence and retention metrics for Power BI and clinical program reviews.
    """
    total_appointments: int = Field(..., ge=0, description="Total appointments considered")
    scheduled_count: int = Field(..., ge=0, description="Appointments currently scheduled")
    completed_count: int = Field(..., ge=0, description="Appointments successfully completed")
    missed_count: int = Field(..., ge=0, description="Appointments missed without notice")
    cancelled_count: int = Field(..., ge=0, description="Appointments cancelled")
    rescheduled_count: int = Field(..., ge=0, description="Appointments rescheduled")
    completion_rate: float = Field(..., ge=0.0, le=100.0, description="Percentage of finalized appointments completed")
    missed_rate: float = Field(..., ge=0.0, le=100.0, description="Percentage of finalized appointments missed")
    by_type: Dict[str, int] = Field(default_factory=dict, description="Count of appointments by type")


class AppointmentAnalyticsResponse(DataResponse[AppointmentAnalyticsRead]):
    """Standard envelope for appointment analytics."""
    pass


class EscalationSummaryMetrics(BaseModel):
    """Summary of clinical/human escalations and turnaround time."""
    total_escalations: int = Field(..., ge=0, description="Total recorded escalations")
    open_count: int = Field(..., ge=0, description="Currently open escalations")
    resolved_count: int = Field(..., ge=0, description="Resolved escalations")
    by_category: Dict[str, int] = Field(default_factory=dict, description="Breakdown by escalation category")
    avg_resolution_hours: float = Field(default=0.0, ge=0.0, description="Average turnaround hours for resolved escalations")


class FollowUpSummaryMetrics(BaseModel):
    """Summary of follow-up tasks and care re-engagement progress."""
    total_followups: int = Field(..., ge=0, description="Total follow-up tasks created")
    pending_count: int = Field(..., ge=0, description="Pending follow-up tasks")
    completed_count: int = Field(..., ge=0, description="Completed follow-up tasks")
    completion_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Follow-up task completion percentage")


class EngagementAnalyticsRead(BaseModel):
    """
    Communication volume, barrier distribution, and care engagement analytics for Power BI.
    """
    total_interactions: int = Field(..., ge=0, description="Total recorded interactions")
    incoming_count: int = Field(..., ge=0, description="Inbound client messages")
    outgoing_count: int = Field(..., ge=0, description="Outbound outreach and automated responses")
    by_channel: Dict[str, int] = Field(default_factory=dict, description="Interaction volume by channel")
    by_type: Dict[str, int] = Field(default_factory=dict, description="Interaction volume by interaction type")
    by_intent: Dict[str, int] = Field(default_factory=dict, description="Distribution of classified AI intents")
    barrier_breakdown: Dict[str, int] = Field(default_factory=dict, description="Frequency of reported non-clinical barriers")
    escalation_metrics: EscalationSummaryMetrics = Field(..., description="Escalation turnaround and category metrics")
    followup_metrics: FollowUpSummaryMetrics = Field(..., description="Follow-up task completion metrics")


class EngagementAnalyticsResponse(DataResponse[EngagementAnalyticsRead]):
    """Standard envelope for engagement analytics."""
    pass
