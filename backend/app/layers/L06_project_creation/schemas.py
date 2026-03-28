"""Layer 6: Request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.layers.L06_project_creation.models import ProjectStatus, RealizationStage


class ProjectCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str = ""
    module_id: uuid.UUID | None = None


class ProjectUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: ProjectStatus | None = None
    realization_stage: RealizationStage | None = None


class MilestoneCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str = ""


class MilestoneUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    completed: bool | None = None


class MilestoneResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    position: int
    completed: bool

    model_config = {"from_attributes": True}


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    file_url: str
    file_type: str
    uploaded_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    created_by: uuid.UUID
    module_id: uuid.UUID | None
    realization_stage: RealizationStage
    status: ProjectStatus

    model_config = {"from_attributes": True}


class ProjectDetailResponse(ProjectResponse):
    milestones: list[MilestoneResponse] = []
    artifacts: list[ArtifactResponse] = []
