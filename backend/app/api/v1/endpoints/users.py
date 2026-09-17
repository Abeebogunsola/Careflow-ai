"""
User and Role Endpoints.

Source of truth: docs/database-design.md - Section 6 & 7.
Provides read/write access for user management and staff assignment without exposing secrets.
Full JWT authentication is intentionally deferred to Phase 7/future phases.
"""

import hashlib
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.common import DataResponse, PaginatedResponse, PaginationMeta
from app.schemas.user import RoleRead, UserCreate, UserRead
from app.services.audit import record_audit

router = APIRouter(prefix="", tags=["Users & Roles"])


def _hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a unique random salt.
    Plaintext passwords must NEVER be persisted.
    """
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"pbkdf2:sha256:100000${salt.hex()}${dk.hex()}"


@router.get(
    "/roles",
    response_model=DataResponse[List[RoleRead]],
    summary="List system roles",
)
def list_roles(
    db: Session = Depends(get_db),
) -> DataResponse[List[RoleRead]]:
    """
    Lists all available system roles (e.g., admin, staff, client).
    """
    roles = db.execute(select(Role).order_by(Role.name)).scalars().all()
    return DataResponse(data=[RoleRead.model_validate(r) for r in roles])


@router.get(
    "/users",
    response_model=PaginatedResponse[UserRead],
    summary="List users",
)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role_id: Optional[uuid.UUID] = Query(None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[UserRead]:
    """
    Returns a paginated list of users. Passwords are strictly omitted.
    """
    query = select(User)

    if role_id is not None:
        query = query.where(User.role_id == role_id)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    items = db.execute(
        query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    ).scalars().all()

    return PaginatedResponse(
        data=[UserRead.model_validate(u) for u in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
        ),
    )


@router.get(
    "/users/{user_id}",
    response_model=DataResponse[UserRead],
    summary="Get user by ID",
)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DataResponse[UserRead]:
    """
    Retrieves a user by UUID. Passwords are strictly omitted.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return DataResponse(data=UserRead.model_validate(user))


@router.post(
    "/users",
    response_model=DataResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> DataResponse[UserRead]:
    """
    Creates a new user with a hashed password.
    """
    role = db.get(Role, payload.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referenced role does not exist.",
        )

    # Check email uniqueness
    existing_user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{payload.email}' already exists.",
        )

    user = User(
        role_id=payload.role_id,
        email=payload.email,
        password_hash=_hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        is_active=payload.is_active,
    )
    db.add(user)
    db.flush()

    record_audit(
        db,
        action="user_created",
        entity_type="user",
        entity_id=user.id,
        metadata={"email": user.email, "role": role.name},
    )
    db.commit()
    db.refresh(user)

    return DataResponse(data=UserRead.model_validate(user))
