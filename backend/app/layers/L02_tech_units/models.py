"""Layer 2: Tech unit and chain models."""

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import AuditBase


class TechUnit(AuditBase):
    """A technological unit at a specific knowledge level."""

    __tablename__ = "tech_unit"

    level_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_level.id"), nullable=False)
    name_de: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_de: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    io_spec: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    limitations: Mapped[str] = mapped_column(Text, default="")


class TechUnitChain(AuditBase):
    """A sequence of tech units chained together."""

    __tablename__ = "tech_unit_chain"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_level.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")

    links = relationship("TechUnitChainLink", back_populates="chain", order_by="TechUnitChainLink.position")


class TechUnitChainLink(AuditBase):
    """A link in a tech unit chain (ordering of units)."""

    __tablename__ = "tech_unit_chain_link"

    chain_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tech_unit_chain.id"), nullable=False)
    tech_unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tech_unit.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    chain = relationship("TechUnitChain", back_populates="links")
