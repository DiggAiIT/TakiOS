"""Layer 10: I/O capability and user preference models."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class IOType(str, enum.Enum):
    VOICE = "voice"
    TOUCH = "touch"
    TEXT = "text"
    VISUAL = "visual"


class IOCapability(AuditBase):
    __tablename__ = "io_capability"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[IOType] = mapped_column(Enum(IOType), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class UserIOPreference(AuditBase):
    __tablename__ = "user_io_preference"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    input_mode: Mapped[IOType] = mapped_column(Enum(IOType), default=IOType.TEXT)
    output_mode: Mapped[IOType] = mapped_column(Enum(IOType), default=IOType.TEXT)
