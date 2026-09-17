"""
API v1 Router Aggregator.

Centralizes and mounts all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    clients,
    appointments,
    interactions,
    followups,
    escalations,
    approved_info,
    audit_logs,
    users,
)

api_router = APIRouter()

# Mount all domain endpoint routers
api_router.include_router(health.router)
api_router.include_router(clients.router)
api_router.include_router(appointments.router)
api_router.include_router(interactions.router)
api_router.include_router(followups.router)
api_router.include_router(escalations.router)
api_router.include_router(approved_info.router)
api_router.include_router(audit_logs.router)
api_router.include_router(users.router)
