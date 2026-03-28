"""Shared pagination schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response envelope."""

    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, per_page: int) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=(total + per_page - 1) // per_page if per_page > 0 else 0,
        )
