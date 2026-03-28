"""Layer 9: Stage gate criteria and project realization models."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class RealizationStage(str, enum.Enum):
    IDEA = "idea"
    CONCEPT = "concept"
    MVP = "mvp"
    PROTOTYPE_2D = "2d"
    PROTOTYPE_3D = "3d"
    REAL_WORLD = "real_world"
    LIFECYCLE = "lifecycle"


class StageGateCriteria(AuditBase):
    __tablename__ = "stage_gate_criteria"

    stage: Mapped[RealizationStage] = mapped_column(Enum(RealizationStage), nullable=False)
    criteria: Mapped[dict] = mapped_column(JSONB, default=dict)
    required_artifacts: Mapped[dict] = mapped_column(JSONB, default=list)


class ProjectRealization(AuditBase):
    __tablename__ = "project_realization"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project.id"), nullable=False)
    stage: Mapped[RealizationStage] = mapped_column(Enum(RealizationStage), nullable=False)
    evidence: Mapped[str] = mapped_column(Text, default="")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user.id"), nullable=True)
