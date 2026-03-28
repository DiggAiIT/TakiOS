"""Layer 1: Knowledge level and user progress models."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import AuditBase


class LevelStatus(str, enum.Enum):
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class KnowledgeLevel(AuditBase):
    """A level on the knowledge pyramid (e.g., Binary, Logic Gates, Programming, AI)."""

    __tablename__ = "knowledge_level"

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("knowledge_level.id"), nullable=True
    )
    name_de: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_de: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    pyramid_position: Mapped[int] = mapped_column(Integer, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    unlock_criteria: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    children = relationship("KnowledgeLevel", back_populates="parent")
    parent = relationship("KnowledgeLevel", back_populates="children", remote_side="KnowledgeLevel.id")


class UserLevelProgress(AuditBase):
    """Tracks a user's progress on a specific knowledge level."""

    __tablename__ = "user_level_progress"
    __table_args__ = (UniqueConstraint("user_id", "level_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    level_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_level.id"), nullable=False)
    status: Mapped[LevelStatus] = mapped_column(
        Enum(LevelStatus), default=LevelStatus.LOCKED, nullable=False
    )
