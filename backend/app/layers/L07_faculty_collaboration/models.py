"""Layer 7: Faculty profiles and review models."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    DECLINED = "declined"


class FacultyProfile(AuditBase):
    __tablename__ = "faculty_profile"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(255), default="")
    expertise_areas: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    available_for_review: Mapped[bool] = mapped_column(Boolean, default=True)


class ReviewRequest(AuditBase):
    __tablename__ = "review_request"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project.id"), nullable=False)
    faculty_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("faculty_profile.id"), nullable=False)
    requested_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    review_text: Mapped[str | None] = mapped_column(Text, nullable=True)
