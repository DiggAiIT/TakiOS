"""Layer 13: Request/response schemas."""

import uuid
from typing import Any

from pydantic import BaseModel

from app.layers.L13_social_engineering_impact.models import RiskLevel


class ImpactAssessmentResponse(BaseModel):
    id: uuid.UUID
    title: str
    category: str
    description: str
    risk_level: RiskLevel
    mitigation: str

    model_config = {"from_attributes": True}


class SurveyResponse(BaseModel):
    id: uuid.UUID
    title: str
    questions: list[Any]

    model_config = {"from_attributes": True}


class SurveyResponseCreate(BaseModel):
    survey_id: uuid.UUID
    responses: dict[str, Any]


class SurveyResponseOut(BaseModel):
    id: uuid.UUID
    survey_id: uuid.UUID
    user_id: uuid.UUID
    responses: dict[str, Any]

    model_config = {"from_attributes": True}
