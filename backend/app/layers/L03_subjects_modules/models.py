"""Layer 3: Subject, module, and curriculum models."""

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import AuditBase


class Subject(AuditBase):
    """An academic discipline (e.g., Anatomie, Physik, Informatik)."""

    __tablename__ = "subject"

    name_de: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_de: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(String(255), default="Medizintechnik")

    modules = relationship("Module", back_populates="subject")


class Module(AuditBase):
    """A course module within a subject (e.g., Anatomie I, semester 1)."""

    __tablename__ = "module"

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subject.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_de: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=5)
    description_de: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")

    subject = relationship("Subject", back_populates="modules")
    units = relationship("ModuleUnit", back_populates="module", order_by="ModuleUnit.position")


class ModuleUnit(AuditBase):
    """A learning unit within a module (individual topic/lesson)."""

    __tablename__ = "module_unit"

    module_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("module.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title_de: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)

    module = relationship("Module", back_populates="units")


class ModulePrerequisite(AuditBase):
    """Prerequisite relationship between modules."""

    __tablename__ = "module_prerequisite"

    module_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("module.id"), nullable=False)
    prerequisite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("module.id"), nullable=False)
