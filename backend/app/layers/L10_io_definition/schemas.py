"""Layer 10: Request/response schemas."""

import uuid

from pydantic import BaseModel

from app.layers.L10_io_definition.models import IOType


class IOCapabilityResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: IOType
    enabled: bool

    model_config = {"from_attributes": True}


class UserIOPreferenceUpdate(BaseModel):
    input_mode: IOType | None = None
    output_mode: IOType | None = None


class UserIOPreferenceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    input_mode: IOType
    output_mode: IOType

    model_config = {"from_attributes": True}
