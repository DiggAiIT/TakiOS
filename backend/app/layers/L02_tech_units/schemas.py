"""Layer 2: Request/response schemas."""

import uuid

from pydantic import BaseModel


class TechUnitResponse(BaseModel):
    id: uuid.UUID
    level_id: uuid.UUID
    name_de: str
    name_en: str
    description_de: str
    description_en: str
    io_spec: dict | None
    limitations: str

    model_config = {"from_attributes": True}


class TechUnitChainResponse(BaseModel):
    id: uuid.UUID
    name: str
    level_id: uuid.UUID
    description: str
    units: list[TechUnitResponse] = []

    model_config = {"from_attributes": True}
