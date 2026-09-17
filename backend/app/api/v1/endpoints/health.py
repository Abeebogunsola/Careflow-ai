"""
Health Check Endpoint for CareFlow AI.

Provides service and database operational status.
Follows docs/api.md - Section 14 and Phase 4 Database requirements.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

router = APIRouter()


class HealthData(BaseModel):
    status: str = Field(default="ok", description="Operational status of the API service")
    database: str = Field(..., description="Operational status of the database connection ('ok' or 'unavailable')")
    service: str = Field(default=settings.PROJECT_NAME, description="Service name")
    version: str = Field(default=settings.VERSION, description="Application version")


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Overall health status")
    data: HealthData = Field(..., description="Health payload details")


def check_database_connection() -> str:
    """
    Attempts a lightweight query to verify database connectivity.
    Returns 'ok' on success, or 'unavailable' if unreachable.
    Does not raise exceptions to ensure API service remains operational.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return "ok"
    except Exception:
        return "unavailable"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check operational status of the API service and database connectivity.",
)
def health_check() -> HealthResponse:
    """
    Returns API service status and database connectivity status.
    """
    db_status = check_database_connection()

    return HealthResponse(
        status="ok",
        data=HealthData(
            status="ok",
            database=db_status,
            service=settings.PROJECT_NAME,
            version=settings.VERSION,
        ),
    )
