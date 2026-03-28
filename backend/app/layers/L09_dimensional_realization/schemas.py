"""Layer 9: Request/response schemas."""

import uuid
from typing import Any

from pydantic import BaseModel

from app.layers.L09_dimensional_realization.models import RealizationStage


class StageGateCriteriaResponse(BaseModel):
    id: uuid.UUID
    stage: RealizationStage
    criteria: dict[str, Any]
    required_artifacts: list[Any]

    model_config = {"from_attributes": True}


class AdvanceStageRequest(BaseModel):
    project_id: uuid.UUID
    target_stage: RealizationStage
    evidence: str = ""


class ProjectRealizationResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    stage: RealizationStage
    evidence: str
    approved_by: uuid.UUID | None

    model_config = {"from_attributes": True}
