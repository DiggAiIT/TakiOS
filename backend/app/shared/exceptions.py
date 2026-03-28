"""Application-wide exception definitions."""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class APIErrorResponse(BaseModel):
    """Standardised error envelope returned by all endpoints (EU AI Act Art. 12 traceability)."""

    error_code: str = Field(..., description="Machine-readable error code, e.g. NOT_FOUND")
    detail_de: str = Field(..., description="Human-readable German message")
    detail_en: str = Field(..., description="Human-readable English message")
    request_id: str = Field(default="unknown", description="Correlation ID from X-Request-Id header")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC ISO-8601 timestamp",
    )


class NotFoundError(HTTPException):
    def __init__(self, entity: str, entity_id: str | None = None) -> None:
        detail = f"{entity} not found"
        if entity_id:
            detail = f"{entity} with id '{entity_id}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "You do not have permission to perform this action") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class PayloadTooLargeError(HTTPException):
    def __init__(self, detail: str = "Payload too large") -> None:
        super().__init__(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=detail)
