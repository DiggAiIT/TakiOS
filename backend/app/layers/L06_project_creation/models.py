"""Layer 6: Project, milestone, and artifact models."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import AuditBase


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RealizationStage(str, enum.Enum):
    IDEA = "idea"
    CONCEPT = "concept"
    MVP = "mvp"
    PROTOTYPE_2D = "2d"
    PROTOTYPE_3D = "3d"
    REAL_WORLD = "real_world"
    LIFECYCLE = "lifecycle"


class Project(AuditBase):
    __tablename__ = "project"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    module_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("module.id"), nullable=True)
    realization_stage: Mapped[RealizationStage] = mapped_column(
        Enum(RealizationStage), default=RealizationStage.IDEA
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.DRAFT
    )

    milestones = relationship("ProjectMilestone", back_populates="project")
    artifacts = relationship("ProjectArtifact", back_populates="project")


class ProjectMilestone(AuditBase):
    __tablename__ = "project_milestone"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)

    project = relationship("Project", back_populates="milestones")


class ProjectArtifact(AuditBase):
    __tablename__ = "project_artifact"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    project = relationship("Project", back_populates="artifacts")
