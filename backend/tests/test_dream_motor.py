"""Tests for the AutoDream background motor."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tasks.dream_motor import _load_dream_prompt, async_dream_cycle


class TestLoadDreamPrompt:
    """Test dream prompt template loading."""

    def test_loads_from_file(self):
        prompt = _load_dream_prompt()
        assert "system" in prompt
        assert "template" in prompt
        assert isinstance(prompt["system"], str)
        assert isinstance(prompt["template"], str)

    def test_system_prompt_not_empty(self):
        prompt = _load_dream_prompt()
        assert len(prompt["system"]) > 0

    def test_template_has_placeholders(self):
        prompt = _load_dream_prompt()
        assert "{existing_index}" in prompt["template"]
        assert "{new_entries}" in prompt["template"]
        assert "{max_lines}" in prompt["template"]


class TestDreamCycleNoWork:
    """Test dream cycle when there's nothing to process."""

    @pytest.mark.asyncio
    async def test_no_sessions_returns_no_work(self):
        """Dream cycle with no unprocessed sessions returns early."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        mock_db.scalar.return_value = 0

        with patch(
            "app.tasks.dream_motor.async_session"
        ) as mock_session_factory:
            mock_ctx = (
                mock_session_factory.return_value.__aenter__
            ) = AsyncMock(return_value=mock_db)
            mock_session_factory.return_value.__aexit__ = AsyncMock(
                return_value=False
            )

            # The function manages its own session,
            # so we patch at the service level
            with patch(
                "app.tasks.dream_motor"
                ".MemoryService.get_unprocessed_sessions",
                new_callable=AsyncMock,
                return_value=[],
            ):
                result = await async_dream_cycle({})

        assert result["status"] == "no_work"
        assert result["sessions_processed"] == 0


class TestDreamCycleSafety:
    """Test that dream cycle respects safety constraints."""

    def test_dream_prompt_forbids_code_access(self):
        """Dream prompt should not reference source code paths."""
        prompt = _load_dream_prompt()
        full_text = json.dumps(prompt).lower()
        # Should not contain instructions to access source code
        assert "import " not in prompt["template"]
        assert "exec(" not in prompt["template"]
        assert "eval(" not in prompt["template"]
