"""
Analytics Schemas for CareFlow AI.

Source of truth: docs/api.md - Section 25 and docs/workflows.md - Workflow 11.
Provides aggregate program-level metrics with zero personally identifiable information.
"""

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
