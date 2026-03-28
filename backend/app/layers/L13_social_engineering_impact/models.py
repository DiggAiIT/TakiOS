"""Layer 13: Impact assessment and survey models."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactAssessment(AuditBase):
    __tablename__ = "impact_assessment"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), default=RiskLevel.LOW)
    mitigation: Mapped[str] = mapped_column(Text, default="")


class Survey(AuditBase):
    __tablename__ = "survey"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    questions: Mapped[dict] = mapped_column(JSONB, default=list)


class SurveyResponse(AuditBase):
    __tablename__ = "survey_response"

    survey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("survey.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    responses: Mapped[dict] = mapped_column(JSONB, default=dict)
