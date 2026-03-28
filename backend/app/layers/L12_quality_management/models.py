"""Layer 12: Quality metric, measurement, and feedback models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class QualityMetric(AuditBase):
    __tablename__ = "quality_metric"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="")


class QualityMeasurement(AuditBase):
    __tablename__ = "quality_measurement"

    metric_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quality_metric.id"), nullable=False)
    measured_value: Mapped[float] = mapped_column(Float, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserFeedback(AuditBase):
    __tablename__ = "user_feedback"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
