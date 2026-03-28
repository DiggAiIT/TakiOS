"""Layer 3: Request/response schemas."""

import uuid

from pydantic import BaseModel, Field


class SubjectResponse(BaseModel):
    id: uuid.UUID
    name_de: str
    name_en: str
    description_de: str
    description_en: str
    department: str

    model_config = {"from_attributes": True}


class ModuleUnitResponse(BaseModel):
    id: uuid.UUID
    position: int
    title_de: str
    title_en: str

    model_config = {"from_attributes": True}


class ModuleResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    code: str
    name_de: str
    name_en: str
    semester: int
    credits: int
    description_de: str
    description_en: str

    model_config = {"from_attributes": True}


class ModuleDetailResponse(ModuleResponse):
    units: list[ModuleUnitResponse] = []


class ModuleCreate(BaseModel):
    subject_id: uuid.UUID
    code: str = Field(max_length=50)
    name_de: str = Field(max_length=255)
    name_en: str = Field(max_length=255)
    semester: int = Field(ge=1, le=10)
    credits: int = Field(default=5, ge=1)
    description_de: str = ""
    description_en: str = ""
