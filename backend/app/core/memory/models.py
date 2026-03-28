"""SQLAlchemy models for the hierarchical memory system."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import AuditBase


class MemoryLayer(str, enum.Enum):
    """Memory storage layer classification."""

    active = "active"
    automemory = "automemory"
    autodream = "autodream"


class MemoryEntryStatus(str, enum.Enum):
    """Lifecycle status of a memory entry."""

    active = "active"
    archived = "archived"
    pruned = "pruned"


class MemorySession(AuditBase):
    """Tracks an agent interaction session for memory recording."""

    __tablename__ = "memory_session"

    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    task_summary: Mapped[str] = mapped_column(Text, default="")
    turn_count: Mapped[int] = mapped_column(Integer, default=0)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0)
    is_dream_processed: Mapped[bool] = mapped_column(default=False, index=True)

    entries: Mapped[list["MemoryEntry"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class MemoryEntry(AuditBase):
    """Individual memory record within a session."""

    __tablename__ = "memory_entry"

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_session.id"), nullable=False, index=True
    )
    layer: Mapped[MemoryLayer] = mapped_column(
        Enum(MemoryLayer), nullable=False, default=MemoryLayer.automemory, index=True
    )
    status: Mapped[MemoryEntryStatus] = mapped_column(
        Enum(MemoryEntryStatus), nullable=False, default=MemoryEntryStatus.active
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    compacted_line: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="general", index=True)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped["MemorySession"] = relationship(back_populates="entries")


class MemoryIndex(AuditBase):
    """Compacted memory index maintained by the Dream Sub-agent.

    Each row is a single one-line entry in the compacted index.
    The Dream Sub-agent is the sole writer; all other agents have read-only access.
    """

    __tablename__ = "memory_index"

    line_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general", index=True)
    source_entry_ids: Mapped[str] = mapped_column(
        Text, default="", doc="Comma-separated UUIDs of source MemoryEntry records"
    )
    dream_cycle: Mapped[int] = mapped_column(
        Integer, default=0, doc="Which dream cycle produced this index line"
    )
