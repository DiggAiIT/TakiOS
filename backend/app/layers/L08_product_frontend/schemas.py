"""Layer 8: Request/response schemas."""

import uuid

from pydantic import BaseModel, Field


class UserPreferenceUpdate(BaseModel):
    theme: str | None = Field(None, max_length=50)
    high_contrast: bool | None = None
    reduced_motion: bool | None = None
    font_size: int | None = Field(None, ge=8, le=48)
    locale: str | None = Field(None, max_length=10)


class UserPreferenceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    theme: str
    high_contrast: bool
    reduced_motion: bool
    font_size: int
    locale: str

    model_config = {"from_attributes": True}
