"""
Appointment Endpoints.

Source of truth: docs/api.md - Section 17 & docs/database-design.md - Section 11 & 12.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.client import Client
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentRead
from app.services.audit import record_audit

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post(
    "",
    response_model=DataResponse[AppointmentRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create an appointment",
)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
) -> DataResponse[AppointmentRead]:
    """
    Creates an appointment for an existing client.
    """
    client = db.get(Client, payload.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referenced client does not exist.",
        )

    appointment = Appointment(
        client_id=payload.client_id,
        appointment_type=payload.appointment_type,
        scheduled_at=payload.scheduled_at,
        status=payload.status.value,
        location_label=payload.location_label,
    )
    db.add(appointment)
    db.flush()

    record_audit(
        db,
        action="appointment_created",
        entity_type="appointment",
        entity_id=appointment.id,
        metadata={"client_id": str(payload.client_id), "status": appointment.status},
    )
    db.commit()
    db.refresh(appointment)

    return DataResponse(data=AppointmentRead.model_validate(appointment))


@router.get(
    "",
    response_model=PaginatedResponse[AppointmentRead],
    summary="List appointments",
)
def list_appointments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by appointment status"),
    start_date: Optional[datetime] = Query(None, description="Filter scheduled_at on or after this timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter scheduled_at on or before this timestamp"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AppointmentRead]:
    """
    Returns a paginated list of appointments with optional filtering.
    """
    query = select(Appointment)

    if client_id is not None:
        query = query.where(Appointment.client_id == client_id)
    if status is not None:
        query = query.where(Appointment.status == status.value)
    if start_date is not None:
        query = query.where(Appointment.scheduled_at >= start_date)
    if end_date is not None:
        query = query.where(Appointment.scheduled_at <= end_date)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(Appointment.scheduled_at.asc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[AppointmentRead.model_validate(a) for a in items],
        pagination=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get(
    "/{appointment_id}",
    response_model=DataResponse[AppointmentRead],
    summary="Get an appointment by ID",
)
def get_appointment(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[AppointmentRead]:
    """
    Retrieves details of a specific appointment.
    """
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found.",
        )
    return DataResponse(data=AppointmentRead.model_validate(appointment))


@router.patch(
    "/{appointment_id}",
    response_model=DataResponse[AppointmentRead],
    summary="Update an appointment",
)
def update_appointment(
    appointment_id: uuid.UUID,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
) -> DataResponse[AppointmentRead]:
    """
    Updates appointment state, scheduled time, or location.
    """
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found.",
        )

    if payload.appointment_type is not None:
        appointment.appointment_type = payload.appointment_type
    if payload.scheduled_at is not None:
        appointment.scheduled_at = payload.scheduled_at
    if payload.status is not None:
        appointment.status = payload.status.value
    if payload.location_label is not None:
        appointment.location_label = payload.location_label

    record_audit(
        db,
        action="appointment_updated",
        entity_type="appointment",
        entity_id=appointment.id,
        metadata={"status": appointment.status},
    )
    db.commit()
    db.refresh(appointment)

    return DataResponse(data=AppointmentRead.model_validate(appointment))
