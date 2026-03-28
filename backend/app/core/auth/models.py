"""User model and role definitions."""

import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import AuditBase


class UserRole(str, enum.Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"


class User(AuditBase):
    """Core user model for authentication and authorization."""

    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.STUDENT, nullable=False
    )
    locale: Mapped[str] = mapped_column(String(5), default="de", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
