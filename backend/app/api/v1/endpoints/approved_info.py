"""
Approved Information Endpoints.

Source of truth: docs/api.md - Section 24 & docs/database-design.md - Section 24 & 25.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.approved_info import ApprovedInformation
from app.models.enums import ApprovedInfoCategory
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.approved_info import (
    ApprovedInformationCreate,
    ApprovedInformationUpdate,
    ApprovedInformationRead,
)
from app.services.audit import record_audit

router = APIRouter(prefix="/approved-information", tags=["Approved Information"])


@router.post(
    "",
    response_model=DataResponse[ApprovedInformationRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create approved information",
)
def create_approved_information(
    payload: ApprovedInformationCreate,
    db: Session = Depends(get_db),
) -> DataResponse[ApprovedInformationRead]:
    """
    Creates an approved clinical/program information entry.
    Only authorized administrators can publish approved content for the AI agent to reference.
    """
    info = ApprovedInformation(
        title=payload.title,
        category=payload.category.value,
        content=payload.content,
        version=payload.version,
        is_active=payload.is_active,
    )
    db.add(info)
    db.flush()

    record_audit(
        db,
        action="approved_information_created",
        entity_type="approved_information",
        entity_id=info.id,
        metadata={"title": info.title, "category": info.category, "version": info.version},
    )
    db.commit()
    db.refresh(info)

    return DataResponse(data=ApprovedInformationRead.model_validate(info))


@router.get(
    "",
    response_model=PaginatedResponse[ApprovedInformationRead],
    summary="List approved information",
)
def list_approved_information(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[ApprovedInfoCategory] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ApprovedInformationRead]:
    """
    Returns a paginated list of approved information entries.
    """
    query = select(ApprovedInformation)

    if category is not None:
        query = query.where(ApprovedInformation.category == category.value)
    if is_active is not None:
        query = query.where(ApprovedInformation.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(ApprovedInformation.created_at.desc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[ApprovedInformationRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
        ),
    )


@router.get(
    "/{information_id}",
    response_model=DataResponse[ApprovedInformationRead],
    summary="Get approved information by ID",
)
def get_approved_information(
    information_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[ApprovedInformationRead]:
    """
    Retrieves a single approved information record by its UUID.
    """
    info = db.get(ApprovedInformation, information_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approved information with ID {information_id} not found.",
        )
    return DataResponse(data=ApprovedInformationRead.model_validate(info))


@router.patch(
    "/{information_id}",
    response_model=DataResponse[ApprovedInformationRead],
    summary="Update approved information",
)
def update_approved_information(
    information_id: uuid.UUID,
    payload: ApprovedInformationUpdate,
    db: Session = Depends(get_db),
) -> DataResponse[ApprovedInformationRead]:
    """
    Updates an approved information entry (title, category, content, version, or active status).
    """
    info = db.get(ApprovedInformation, information_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approved information with ID {information_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "category" and value is not None:
            info.category = value.value if hasattr(value, "value") else str(value)
        else:
            setattr(info, field, value)

    record_audit(
        db,
        action="approved_information_updated",
        entity_type="approved_information",
        entity_id=info.id,
        metadata={"updated_fields": list(update_data.keys()), "version": info.version},
    )
    db.commit()
    db.refresh(info)

    return DataResponse(data=ApprovedInformationRead.model_validate(info))
