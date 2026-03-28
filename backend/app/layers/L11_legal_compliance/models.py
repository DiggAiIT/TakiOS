"""Layer 11: Compliance requirement and evidence models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class ComplianceRequirement(AuditBase):
    __tablename__ = "compliance_requirement"

    framework: Mapped[str] = mapped_column(String(100), nullable=False)
    clause: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    applies_to: Mapped[str] = mapped_column(String(255), default="")


class ComplianceEvidence(AuditBase):
    __tablename__ = "compliance_evidence"

    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compliance_requirement.id"), nullable=False
    )
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    verified_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
