"""Layer 11: Request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ComplianceRequirementResponse(BaseModel):
    id: uuid.UUID
    framework: str
    clause: str
    title: str
    description: str
    applies_to: str

    model_config = {"from_attributes": True}


class ComplianceEvidenceCreate(BaseModel):
    requirement_id: uuid.UUID
    evidence_type: str = Field(max_length=100)
    description: str = ""


class ComplianceEvidenceResponse(BaseModel):
    id: uuid.UUID
    requirement_id: uuid.UUID
    evidence_type: str
    description: str
    verified_by: uuid.UUID | None
    verified_at: datetime | None

    model_config = {"from_attributes": True}


class ComplianceStatusResponse(BaseModel):
    total_requirements: int
    evidenced_requirements: int
    verified_requirements: int
    compliance_percentage: float
