"""
Common Response, Pagination, and Error Schemas.

Source of truth: docs/api.md - Section 12 & 13.
"""

from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total number of matching records")


class DataResponse(BaseModel, Generic[T]):
    data: T = Field(..., description="Response payload")


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T] = Field(..., description="List of items for current page")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Standard machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[Any] = Field(default=None, description="Optional context or validation details")


class ErrorResponse(BaseModel):
    error: ErrorDetail = Field(..., description="Standard error envelope")
