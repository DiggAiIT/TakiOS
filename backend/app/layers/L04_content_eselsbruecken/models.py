"""Layer 4: Content, mnemonic, and learning profile models."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import AuditBase


class MnemonicType(str, enum.Enum):
    ACRONYM = "acronym"
    STORY = "story"
    VISUAL = "visual"
    RHYME = "rhyme"
    ANALOGY = "analogy"


class Content(AuditBase):
    """Learning content linked to a module unit."""

    __tablename__ = "content"

    module_unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("module_unit.id"), nullable=False
    )
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content_version.id", use_alter=True), nullable=True
    )

    versions = relationship("ContentVersion", back_populates="content", foreign_keys="ContentVersion.content_id")


class ContentVersion(AuditBase):
    """Append-only content versioning for IEC 62304 compliance."""

    __tablename__ = "content_version"

    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content.id"), nullable=False)
    body_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    change_reason: Mapped[str] = mapped_column(Text, default="")

    content = relationship("Content", back_populates="versions", foreign_keys=[content_id])


class Mnemonic(AuditBase):
    """A mnemonic (Eselsbrücke) — personalized or shared."""

    __tablename__ = "mnemonic"

    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content.id"), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    mnemonic_text: Mapped[str] = mapped_column(Text, nullable=False)
    mnemonic_type: Mapped[MnemonicType] = mapped_column(Enum(MnemonicType), nullable=False)
    language: Mapped[str] = mapped_column(String(5), default="de")
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    effectiveness_score: Mapped[float | None] = mapped_column(Float, nullable=True)


class LearningProfile(AuditBase):
    """User's personalized learning profile for Maßschneidung."""

    __tablename__ = "learning_profile"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    learning_style: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    cultural_context: Mapped[str] = mapped_column(String(255), default="")
    preferred_mnemonic_types: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
