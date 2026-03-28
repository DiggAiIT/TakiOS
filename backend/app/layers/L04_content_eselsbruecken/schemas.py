"""Layer 4: Request/response schemas."""

import uuid

from pydantic import BaseModel

from app.layers.L04_content_eselsbruecken.models import MnemonicType


class ContentVersionResponse(BaseModel):
    id: uuid.UUID
    version_number: int
    body_markdown: str
    change_reason: str

    model_config = {"from_attributes": True}


class ContentResponse(BaseModel):
    id: uuid.UUID
    module_unit_id: uuid.UUID
    current_version: ContentVersionResponse | None = None

    model_config = {"from_attributes": True}


class ContentWithBodyResponse(BaseModel):
    id: uuid.UUID
    module_unit_id: uuid.UUID
    body_markdown: str
    mnemonics: list["MnemonicResponse"] = []

    model_config = {"from_attributes": True}


class MnemonicResponse(BaseModel):
    id: uuid.UUID
    content_id: uuid.UUID
    mnemonic_text: str
    mnemonic_type: MnemonicType
    language: str
    ai_generated: bool
    effectiveness_score: float | None

    model_config = {"from_attributes": True}


class GenerateMnemonicRequest(BaseModel):
    content_id: uuid.UUID
    mnemonic_type: MnemonicType = MnemonicType.ANALOGY
    language: str = "de"
    project_context: str | None = None


class RateMnemonicRequest(BaseModel):
    score: float  # 1.0 - 5.0


class LearningProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    learning_style: dict | None
    cultural_context: str
    preferred_mnemonic_types: dict | None

    model_config = {"from_attributes": True}
