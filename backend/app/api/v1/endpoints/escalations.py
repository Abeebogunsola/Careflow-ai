"""
Escalation Endpoints.

Source of truth: docs/api.md - Section 22 & docs/database-design.md - Section 21–23.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.client import Client
from app.models.user import User
from app.models.escalation import Escalation
from app.models.enums import FollowUpPriority, EscalationCategory, EscalationStatus
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.escalation import EscalationCreate, EscalationUpdate, EscalationRead
from app.services.audit import record_audit

router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.post(
    "",
    response_model=DataResponse[EscalationRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create an escalation",
)
def create_escalation(
    payload: EscalationCreate,
    db: Session = Depends(get_db),
) -> DataResponse[EscalationRead]:
    """
    Creates an escalation for human review.
    AI or automated systems route complex or clinical situations to staff through this endpoint.
    """
    client = db.get(Client, payload.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referenced client does not exist.",
        )

    if payload.assigned_to is not None:
        user = db.get(User, payload.assigned_to)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referenced assigned user does not exist.",
            )

    escalation = Escalation(
        client_id=payload.client_id,
        assigned_to=payload.assigned_to,
        category=payload.category.value,
        priority=payload.priority.value,
        reason=payload.reason,
        status=payload.status.value,
    )
    db.add(escalation)
    db.flush()

    record_audit(
        db,
        action="escalation_created",
        entity_type="escalation",
        entity_id=escalation.id,
        metadata={
            "client_id": str(payload.client_id),
            "category": escalation.category,
            "priority": escalation.priority,
            "status": escalation.status,
            "assigned_to": str(payload.assigned_to) if payload.assigned_to else None,
        },
    )
    db.commit()
    db.refresh(escalation)

    return DataResponse(data=EscalationRead.model_validate(escalation))


@router.get(
    "",
    response_model=PaginatedResponse[EscalationRead],
    summary="List escalations",
)
def list_escalations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    status: Optional[EscalationStatus] = Query(None, description="Filter by status"),
    category: Optional[EscalationCategory] = Query(None, description="Filter by category"),
    priority: Optional[FollowUpPriority] = Query(None, description="Filter by priority"),
    assigned_to: Optional[uuid.UUID] = Query(None, description="Filter by assigned user ID"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[EscalationRead]:
    """
    Returns a paginated list of escalations with optional filtering.
    """
    query = select(Escalation)

    if client_id is not None:
        query = query.where(Escalation.client_id == client_id)
    if status is not None:
        query = query.where(Escalation.status == status.value)
    if category is not None:
        query = query.where(Escalation.category == category.value)
    if priority is not None:
        query = query.where(Escalation.priority == priority.value)
    if assigned_to is not None:
        query = query.where(Escalation.assigned_to == assigned_to)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(Escalation.created_at.desc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[EscalationRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
        ),
    )


@router.get(
    "/{escalation_id}",
    response_model=DataResponse[EscalationRead],
    summary="Get escalation by ID",
)
def get_escalation(
    escalation_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[EscalationRead]:
    """
    Retrieves a single escalation by its UUID.
    """
    escalation = db.get(Escalation, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation with ID {escalation_id} not found.",
        )
    return DataResponse(data=EscalationRead.model_validate(escalation))


@router.patch(
    "/{escalation_id}",
    response_model=DataResponse[EscalationRead],
    summary="Update an escalation",
)
def update_escalation(
    escalation_id: uuid.UUID,
    payload: EscalationUpdate,
    db: Session = Depends(get_db),
) -> DataResponse[EscalationRead]:
    """
    Updates an escalation status, priority, reason, or staff assignment.
    """
    escalation = db.get(Escalation, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation with ID {escalation_id} not found.",
        )

    if payload.assigned_to is not None:
        user = db.get(User, payload.assigned_to)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referenced assigned user does not exist.",
            )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value is not None:
            new_status = value.value if hasattr(value, "value") else str(value)
            escalation.status = new_status
            if new_status == EscalationStatus.RESOLVED.value and escalation.resolved_at is None:
                escalation.resolved_at = datetime.now(timezone.utc)
        elif field == "category" and value is not None:
            escalation.category = value.value if hasattr(value, "value") else str(value)
        elif field == "priority" and value is not None:
            escalation.priority = value.value if hasattr(value, "value") else str(value)
        else:
            setattr(escalation, field, value)

    action = "escalation_resolved" if escalation.status == EscalationStatus.RESOLVED.value else "escalation_updated"
    record_audit(
        db,
        action=action,
        entity_type="escalation",
        entity_id=escalation.id,
        metadata={"updated_fields": list(update_data.keys()), "status": escalation.status},
    )
    db.commit()
    db.refresh(escalation)

    return DataResponse(data=EscalationRead.model_validate(escalation))
