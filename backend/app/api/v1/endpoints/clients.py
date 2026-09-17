"""
Client and Communication Preference Endpoints.

Source of truth: docs/api.md - Section 16 & docs/database-design.md - Section 8, 9, 10.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.client import Client
from app.models.communication_preference import CommunicationPreference
from app.models.enums import EnrollmentStatus
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.client import ClientCreate, ClientUpdate, ClientRead
from app.schemas.communication_preference import (
    CommunicationPreferenceCreate,
    CommunicationPreferenceRead,
)
from app.services.audit import record_audit

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post(
    "",
    response_model=DataResponse[ClientRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new client",
)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
) -> DataResponse[ClientRead]:
    """
    Creates a new client record.
    Optionally initializes the client's communication preference if channel is specified.
    """
    if payload.external_reference:
        existing = db.execute(
            select(Client).where(Client.external_reference == payload.external_reference)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client with external reference '{payload.external_reference}' already exists.",
            )

    status_val = payload.status or payload.enrollment_status
    client = Client(
        external_reference=payload.external_reference,
        preferred_name=payload.preferred_name,
        preferred_language=payload.preferred_language,
        enrollment_status=status_val.value if hasattr(status_val, "value") else str(status_val),
        is_active=payload.is_active,
    )
    db.add(client)
    db.flush()

    if payload.communication_channel:
        pref = CommunicationPreference(
            client_id=client.id,
            channel=payload.communication_channel.value,
            is_enabled=True,
        )
        db.add(pref)

    record_audit(
        db,
        action="client_created",
        entity_type="client",
        entity_id=client.id,
        metadata={"external_reference": client.external_reference},
    )
    db.commit()
    db.refresh(client)

    return DataResponse(data=ClientRead.model_validate(client))


@router.get(
    "",
    response_model=PaginatedResponse[ClientRead],
    summary="List clients",
)
def list_clients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[EnrollmentStatus] = Query(None, description="Filter by enrollment status"),
    preferred_language: Optional[str] = Query(None, description="Filter by preferred language"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ClientRead]:
    """
    Returns a paginated collection of clients with optional filtering.
    """
    query = select(Client)

    if status is not None:
        query = query.where(Client.enrollment_status == status.value)
    if preferred_language is not None:
        query = query.where(Client.preferred_language == preferred_language)

    # Calculate total matching count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Fetch page items
    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(Client.created_at.desc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[ClientRead.model_validate(c) for c in items],
        pagination=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get(
    "/{client_id}",
    response_model=DataResponse[ClientRead],
    summary="Get a client by ID",
)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[ClientRead]:
    """
    Retrieves details for a specific client.
    """
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found.",
        )
    return DataResponse(data=ClientRead.model_validate(client))


@router.patch(
    "/{client_id}",
    response_model=DataResponse[ClientRead],
    summary="Update client details",
)
def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
) -> DataResponse[ClientRead]:
    """
    Updates permitted attributes on an existing client.
    """
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found.",
        )

    if payload.external_reference is not None and payload.external_reference != client.external_reference:
        existing = db.execute(
            select(Client).where(Client.external_reference == payload.external_reference)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client with external reference '{payload.external_reference}' already exists.",
            )
        client.external_reference = payload.external_reference

    if payload.preferred_name is not None:
        client.preferred_name = payload.preferred_name
    if payload.preferred_language is not None:
        client.preferred_language = payload.preferred_language
    status_update = payload.status or payload.enrollment_status
    if status_update is not None:
        client.enrollment_status = status_update.value if hasattr(status_update, "value") else str(status_update)
    if payload.is_active is not None:
        client.is_active = payload.is_active

    record_audit(
        db,
        action="client_updated",
        entity_type="client",
        entity_id=client.id,
    )
    db.commit()
    db.refresh(client)

    return DataResponse(data=ClientRead.model_validate(client))


# -----------------------------------------------------------------------------
# Communication Preference Sub-resource
# -----------------------------------------------------------------------------

@router.get(
    "/{client_id}/communication-preference",
    response_model=DataResponse[CommunicationPreferenceRead],
    summary="Get client communication preference",
)
def get_communication_preference(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[CommunicationPreferenceRead]:
    """
    Retrieves the communication channel preference for a client.
    """
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found.",
        )

    pref = db.execute(
        select(CommunicationPreference).where(CommunicationPreference.client_id == client_id)
    ).scalar_one_or_none()

    if not pref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Communication preference not set for this client.",
        )

    return DataResponse(data=CommunicationPreferenceRead.model_validate(pref))


@router.put(
    "/{client_id}/communication-preference",
    response_model=DataResponse[CommunicationPreferenceRead],
    summary="Set or update client communication preference",
)
def set_communication_preference(
    client_id: uuid.UUID,
    payload: CommunicationPreferenceCreate,
    db: Session = Depends(get_db),
) -> DataResponse[CommunicationPreferenceRead]:
    """
    Creates or updates the 1:1 communication preference for a client.
    """
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found.",
        )

    pref = db.execute(
        select(CommunicationPreference).where(CommunicationPreference.client_id == client_id)
    ).scalar_one_or_none()

    channel_input = payload.preferred_channel or payload.channel or CommunicationChannel.WEB
    channel_str = channel_input.value if hasattr(channel_input, "value") else str(channel_input)

    if pref:
        pref.channel = channel_str
        pref.is_enabled = payload.is_enabled
    else:
        pref = CommunicationPreference(
            client_id=client.id,
            channel=channel_str,
            is_enabled=payload.is_enabled,
        )
        db.add(pref)

    record_audit(
        db,
        action="communication_preference_updated",
        entity_type="communication_preference",
        entity_id=pref.id if hasattr(pref, "id") and pref.id else None,
        metadata={"client_id": str(client.id), "channel": channel_str},
    )
    db.commit()
    db.refresh(pref)

    return DataResponse(data=CommunicationPreferenceRead.model_validate(pref))
