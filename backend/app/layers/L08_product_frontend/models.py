"""Layer 8: User preference models for frontend configuration."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class UserPreference(AuditBase):
    __tablename__ = "user_preference"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    theme: Mapped[str] = mapped_column(String(50), default="system")
    high_contrast: Mapped[bool] = mapped_column(Boolean, default=False)
    reduced_motion: Mapped[bool] = mapped_column(Boolean, default=False)
    font_size: Mapped[int] = mapped_column(Integer, default=16)
    locale: Mapped[str] = mapped_column(String(10), default="en")
