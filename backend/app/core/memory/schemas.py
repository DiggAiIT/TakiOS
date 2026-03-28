"""Pydantic schemas for the memory system API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MemoryEntryCreate(BaseModel):
    """Schema for creating a new memory entry."""

    content: str = Field(..., max_length=5000)
    category: str = Field(default="general", max_length=50)


class MemoryEntryResponse(BaseModel):
    """Schema for memory entry API response."""

    id: uuid.UUID
    session_id: uuid.UUID
    layer: str
    status: str
    content: str
    compacted_line: str | None
    category: str
    token_estimate: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemorySessionCreate(BaseModel):
    """Schema for creating a new memory session."""

    agent_name: str = Field(..., max_length=100)
    task_summary: str = Field(default="", max_length=2000)


class MemorySessionResponse(BaseModel):
    """Schema for memory session API response."""

    id: uuid.UUID
    agent_name: str
    task_summary: str
    turn_count: int
    token_estimate: int
    is_dream_processed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemoryIndexLineResponse(BaseModel):
    """Schema for a single compacted index line."""

    id: uuid.UUID
    line_number: int
    content: str
    category: str
    dream_cycle: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemoryIndexResponse(BaseModel):
    """Schema for the full compacted memory index."""

    total_lines: int
    max_lines: int
    dream_cycle: int
    lines: list[MemoryIndexLineResponse]


class MemoryStatusResponse(BaseModel):
    """Schema for memory system status overview."""

    active_sessions: int
    total_entries: int
    unprocessed_sessions: int
    index_lines: int
    max_index_lines: int
    last_dream_cycle: datetime | None
    total_dream_cycles: int


class DreamCycleResponse(BaseModel):
    """Schema for dream cycle execution result."""

    cycle_number: int
    sessions_processed: int
    entries_merged: int
    entries_pruned: int
    index_lines_before: int
    index_lines_after: int
    token_estimate_saved: int
