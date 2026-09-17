"""
Audit Log Endpoints.

Source of truth: docs/api.md - Section 36 & docs/database-design.md - Section 26 & 27.
Immutable and append-only: No PUT, PATCH, or DELETE operations are provided.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.audit_log import AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogRead],
    summary="List audit logs",
)
def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    entity_type: Optional[str] = Query(None, description="Filter by target entity type"),
    entity_id: Optional[uuid.UUID] = Query(None, description="Filter by target entity ID"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AuditLogRead]:
    """
    Returns an append-only audit trail with optional filtering.
    Restricted to authorized administrative/compliance oversight.
    """
    query = select(AuditLog)

    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action is not None:
        query = query.where(AuditLog.action == action)
    if entity_type is not None:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.where(AuditLog.entity_id == entity_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[AuditLogRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
        ),
    )


@router.get(
    "/{log_id}",
    response_model=DataResponse[AuditLogRead],
    summary="Get audit log by ID",
)
def get_audit_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[AuditLogRead]:
    """
    Retrieves a single immutable audit log record by its UUID.
    """
    log_entry = db.get(AuditLog, log_id)
    if not log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit log entry with ID {log_id} not found.",
        )
    return DataResponse(data=AuditLogRead.model_validate(log_entry))
