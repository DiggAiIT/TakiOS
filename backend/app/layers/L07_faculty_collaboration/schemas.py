"""Layer 7: Request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.layers.L07_faculty_collaboration.models import ReviewStatus


class FacultyProfileCreate(BaseModel):
    department: str = Field(max_length=255)
    expertise_areas: list[str] = []


class FacultyProfileUpdate(BaseModel):
    department: str | None = Field(None, max_length=255)
    expertise_areas: list[str] | None = None
    available_for_review: bool | None = None


class FacultyProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    department: str
    expertise_areas: dict | None
    available_for_review: bool

    model_config = {"from_attributes": True}


class ReviewRequestCreate(BaseModel):
    project_id: uuid.UUID
    faculty_id: uuid.UUID


class ReviewRequestResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    faculty_id: uuid.UUID
    requested_by: uuid.UUID
    status: ReviewStatus
    review_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmitReviewRequest(BaseModel):
    review_text: str
