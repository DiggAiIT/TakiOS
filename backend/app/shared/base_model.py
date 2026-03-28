"""Base SQLAlchemy model with audit fields for IEC 62304 traceability."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditBase(Base):
    """Abstract base model with audit fields.

    Every table in TakiOS inherits from this to ensure:
    - UUID primary keys
    - Automatic created_at / updated_at timestamps
    - IEC 62304 traceability via consistent audit trail
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
