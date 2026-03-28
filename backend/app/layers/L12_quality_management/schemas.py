"""Layer 12: Request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QualityMetricResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    target_value: float
    unit: str

    model_config = {"from_attributes": True}


class QualityMeasurementResponse(BaseModel):
    id: uuid.UUID
    metric_id: uuid.UUID
    measured_value: float
    measured_at: datetime

    model_config = {"from_attributes": True}


class QualityDashboardMetric(BaseModel):
    metric_id: uuid.UUID
    name: str
    target_value: float
    latest_value: float | None
    unit: str


class QualityDashboardResponse(BaseModel):
    metrics: list[QualityDashboardMetric]
    total_feedback_count: int
    average_rating: float | None


class UserFeedbackCreate(BaseModel):
    category: str = Field(max_length=100)
    text: str
    rating: int = Field(ge=1, le=5)


class UserFeedbackResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    text: str
    rating: int

    model_config = {"from_attributes": True}
