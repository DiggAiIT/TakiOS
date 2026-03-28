"""Tests for the hierarchical memory service."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core.memory.compactor import MemoryCompactor, is_filler, truncate_to_line
from app.core.memory.models import MemoryEntry, MemoryEntryStatus, MemoryLayer
from app.core.memory.schemas import (
    MemoryEntryCreate,
    MemorySessionCreate,
)


class TestTokenEstimate:
    """Test token estimation heuristic."""

    def test_empty_string(self):
        from app.core.memory.service import _estimate_tokens

        assert _estimate_tokens("") == 1  # min 1

    def test_short_text(self):
        from app.core.memory.service import _estimate_tokens

        assert _estimate_tokens("hello") == 1

    def test_longer_text(self):
        from app.core.memory.service import _estimate_tokens

        text = "a" * 400
        assert _estimate_tokens(text) == 100


class TestFillerDetection:
    """Test conversational filler detection."""

    def test_ok_is_filler(self):
        assert is_filler("ok") is True

    def test_short_text_is_filler(self):
        assert is_filler("yes") is True

    def test_let_me_check_is_filler(self):
        assert is_filler("Let me check that for you") is True

    def test_meaningful_content_is_not_filler(self):
        assert (
            is_filler(
                "The database migration adds three new tables for memory"
            )
            is False
        )

    def test_architectural_decision_is_not_filler(self):
        assert (
            is_filler(
                "Decided to use arq instead of Celery for background tasks"
            )
            is False
        )


class TestTruncateToLine:
    """Test line truncation."""

    def test_short_text_unchanged(self):
        assert truncate_to_line("hello world") == "hello world"

    def test_long_text_truncated(self):
        text = "a" * 200
        result = truncate_to_line(text, max_chars=120)
        assert len(result) == 120
        assert result.endswith("...")

    def test_newlines_removed(self):
        assert truncate_to_line("line1\nline2\nline3") == "line1 line2 line3"

    def test_whitespace_stripped(self):
        assert truncate_to_line("  hello  ") == "hello"


class TestMemoryCompactorLocal:
    """Test local (non-AI) memory compaction."""

    def test_empty_entries_returns_existing_index(self):
        compactor = MemoryCompactor(use_ai=False)
        existing = [{"content": "existing line", "category": "general"}]
        result = compactor.compact_entries_local([], existing)
        assert len(result) == 1
        assert result[0]["content"] == "existing line"

    def test_filler_entries_filtered(self):
        compactor = MemoryCompactor(use_ai=False)
        entries = [
            {"id": "1", "content": "ok", "category": "general"},
            {
                "id": "2",
                "content": "Architectural decision: use PostgreSQL",
                "category": "arch",
            },
        ]
        result = compactor.compact_entries_local(entries, [])
        # Only the meaningful entry should produce an index line
        assert len(result) == 1
        assert "PostgreSQL" in result[0]["content"]

    def test_entries_grouped_by_category(self):
        compactor = MemoryCompactor(use_ai=False)
        entries = [
            {
                "id": "1",
                "content": "First architecture note",
                "category": "architecture",
            },
            {
                "id": "2",
                "content": "Second architecture note",
                "category": "architecture",
            },
            {
                "id": "3",
                "content": "Config change applied",
                "category": "config",
            },
        ]
        result = compactor.compact_entries_local(entries, [])
        categories = {line["category"] for line in result}
        assert "architecture" in categories
        assert "config" in categories

    def test_max_lines_enforced(self):
        compactor = MemoryCompactor(use_ai=False)
        existing = [
            {"content": f"line {i}", "category": "general"}
            for i in range(300)
        ]
        result = compactor.compact_entries_local([], existing)
        from app.config import settings

        assert len(result) <= settings.max_index_lines


class TestMemorySchemas:
    """Test Pydantic schema validation."""

    def test_entry_create_valid(self):
        entry = MemoryEntryCreate(
            content="test content", category="general"
        )
        assert entry.content == "test content"

    def test_entry_create_max_length(self):
        entry = MemoryEntryCreate(content="x" * 5000)
        assert len(entry.content) == 5000

    def test_session_create_valid(self):
        session = MemorySessionCreate(
            agent_name="planner", task_summary="test task"
        )
        assert session.agent_name == "planner"
