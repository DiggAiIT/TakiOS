"""Layer 1: Request/response schemas."""

import uuid

from pydantic import BaseModel

from app.layers.L01_level_selection.models import LevelStatus


class KnowledgeLevelResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID | None
    name_de: str
    name_en: str
    description_de: str
    description_en: str
    pyramid_position: int
    icon_url: str | None
    unlock_criteria: dict | None

    model_config = {"from_attributes": True}


class UserLevelProgressResponse(BaseModel):
    level: KnowledgeLevelResponse
    status: LevelStatus

    model_config = {"from_attributes": True}


class PyramidResponse(BaseModel):
    """Full pyramid structure with user progress."""

    levels: list[KnowledgeLevelResponse]
    progress: dict[str, LevelStatus]  # level_id -> status
