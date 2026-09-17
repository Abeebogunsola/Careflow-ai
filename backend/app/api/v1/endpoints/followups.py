"""
Follow-Up Tasks Endpoints.

Source of truth: docs/api.md - Section 21 & docs/database-design.md - Section 18–20.
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
from app.models.follow_up import FollowUpTask
from app.models.enums import FollowUpPriority, FollowUpStatus
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate, FollowUpRead
from app.services.audit import record_audit

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


@router.post(
    "",
    response_model=DataResponse[FollowUpRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a follow-up task",
)
def create_followup(
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
) -> DataResponse[FollowUpRead]:
    """
    Creates a new follow-up task for an existing client.
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

    followup = FollowUpTask(
        client_id=payload.client_id,
        assigned_to=payload.assigned_to,
        reason=payload.reason,
        priority=payload.priority.value,
        status=payload.status.value,
        due_at=payload.due_at,
    )
    db.add(followup)
    db.flush()

    record_audit(
        db,
        action="followup_created",
        entity_type="follow_up_task",
        entity_id=followup.id,
        metadata={
            "client_id": str(payload.client_id),
            "priority": followup.priority,
            "status": followup.status,
            "assigned_to": str(payload.assigned_to) if payload.assigned_to else None,
        },
    )
    db.commit()
    db.refresh(followup)

    return DataResponse(data=FollowUpRead.model_validate(followup))


@router.get(
    "",
    response_model=PaginatedResponse[FollowUpRead],
    summary="List follow-up tasks",
)
def list_followups(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    status: Optional[FollowUpStatus] = Query(None, description="Filter by task status"),
    priority: Optional[FollowUpPriority] = Query(None, description="Filter by task priority"),
    assigned_to: Optional[uuid.UUID] = Query(None, description="Filter by assigned user ID"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[FollowUpRead]:
    """
    Returns a paginated list of follow-up tasks with optional filtering.
    """
    query = select(FollowUpTask)

    if client_id is not None:
        query = query.where(FollowUpTask.client_id == client_id)
    if status is not None:
        query = query.where(FollowUpTask.status == status.value)
    if priority is not None:
        query = query.where(FollowUpTask.priority == priority.value)
    if assigned_to is not None:
        query = query.where(FollowUpTask.assigned_to == assigned_to)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(FollowUpTask.created_at.desc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[FollowUpRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
        ),
    )


@router.get(
    "/{followup_id}",
    response_model=DataResponse[FollowUpRead],
    summary="Get follow-up task by ID",
)
def get_followup(
    followup_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[FollowUpRead]:
    """
    Retrieves a single follow-up task by its UUID.
    """
    followup = db.get(FollowUpTask, followup_id)
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Follow-up task with ID {followup_id} not found.",
        )
    return DataResponse(data=FollowUpRead.model_validate(followup))


@router.patch(
    "/{followup_id}",
    response_model=DataResponse[FollowUpRead],
    summary="Update a follow-up task",
)
def update_followup(
    followup_id: uuid.UUID,
    payload: FollowUpUpdate,
    db: Session = Depends(get_db),
) -> DataResponse[FollowUpRead]:
    """
    Updates a follow-up task (status, priority, assignment, completion).
    """
    followup = db.get(FollowUpTask, followup_id)
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Follow-up task with ID {followup_id} not found.",
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
            followup.status = new_status
            if new_status == FollowUpStatus.COMPLETED.value and followup.completed_at is None:
                followup.completed_at = datetime.now(timezone.utc)
        elif field == "priority" and value is not None:
            followup.priority = value.value if hasattr(value, "value") else str(value)
        else:
            setattr(followup, field, value)

    action = "followup_completed" if followup.status == FollowUpStatus.COMPLETED.value else "followup_updated"
    record_audit(
        db,
        action=action,
        entity_type="follow_up_task",
        entity_id=followup.id,
        metadata={"updated_fields": list(update_data.keys()), "status": followup.status},
    )
    db.commit()
    db.refresh(followup)

    return DataResponse(data=FollowUpRead.model_validate(followup))
