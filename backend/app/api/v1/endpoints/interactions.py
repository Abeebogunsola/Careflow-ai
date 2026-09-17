"""
Interaction Endpoints.

Source of truth: docs/api.md - Section 18 & docs/database-design.md - Section 14–17.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.client import Client
from app.models.interaction import Interaction
from app.models.enums import (
    CommunicationChannel,
    InteractionDirection,
    InteractionType,
    AIIntentCategory,
)
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.interaction import InteractionCreate, InteractionRead
from app.services.audit import record_audit

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post(
    "",
    response_model=DataResponse[InteractionRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create an interaction",
)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
) -> DataResponse[InteractionRead]:
    """
    Creates an interaction log for an existing client.
    """
    client = db.get(Client, payload.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referenced client does not exist.",
        )

    interaction = Interaction(
        client_id=payload.client_id,
        channel=payload.channel.value,
        direction=payload.direction.value,
        interaction_type=payload.interaction_type.value,
        intent_category=payload.intent_category.value if payload.intent_category else None,
        message_reference=payload.message_reference,
        content=payload.content,
    )
    db.add(interaction)
    db.flush()

    record_audit(
        db,
        action="interaction_created",
        entity_type="interaction",
        entity_id=interaction.id,
        metadata={
            "client_id": str(payload.client_id),
            "channel": interaction.channel,
            "interaction_type": interaction.interaction_type,
            "direction": interaction.direction,
        },
    )
    db.commit()
    db.refresh(interaction)

    return DataResponse(data=InteractionRead.model_validate(interaction))


@router.get(
    "",
    response_model=PaginatedResponse[InteractionRead],
    summary="List interactions",
)
def list_interactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    channel: Optional[CommunicationChannel] = Query(None, description="Filter by channel"),
    direction: Optional[InteractionDirection] = Query(None, description="Filter by direction"),
    interaction_type: Optional[InteractionType] = Query(None, description="Filter by interaction type"),
    intent_category: Optional[AIIntentCategory] = Query(None, description="Filter by AI intent"),
    start_date: Optional[datetime] = Query(None, description="Filter created_at on or after this timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter created_at on or before this timestamp"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[InteractionRead]:
    """
    Returns a paginated list of interactions with optional filtering.
    """
    query = select(Interaction)

    if client_id is not None:
        query = query.where(Interaction.client_id == client_id)
    if channel is not None:
        query = query.where(Interaction.channel == channel.value)
    if direction is not None:
        query = query.where(Interaction.direction == direction.value)
    if interaction_type is not None:
        query = query.where(Interaction.interaction_type == interaction_type.value)
    if intent_category is not None:
        query = query.where(Interaction.intent_category == intent_category.value)
    if start_date is not None:
        query = query.where(Interaction.created_at >= start_date)
    if end_date is not None:
        query = query.where(Interaction.created_at <= end_date)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(Interaction.created_at.desc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[InteractionRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
        ),
    )


@router.get(
    "/{interaction_id}",
    response_model=DataResponse[InteractionRead],
    summary="Get interaction by ID",
)
def get_interaction(
    interaction_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[InteractionRead]:
    """
    Retrieves a single interaction by its UUID.
    """
    interaction = db.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction with ID {interaction_id} not found.",
        )
    return DataResponse(data=InteractionRead.model_validate(interaction))
