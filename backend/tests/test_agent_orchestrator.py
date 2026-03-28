"""Tests for agent orchestration and definition parsing."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.agent_parser import (
    AgentDefinition,
    get_agent,
    load_all_agents,
    parse_agent_file,
    _parse_sections,
)


class TestParseAgentFile:
    """Test markdown agent definition parsing."""

    def test_parse_planner(self, tmp_path):
        md = tmp_path / "test_agent.md"
        md.write_text(
            "---\n"
            "name: test_agent\n"
            "model_routing:\n"
            "  quality: opus\n"
            "  balanced: sonnet\n"
            "  budget: haiku\n"
            "role: planning\n"
            "triggers: manual,temporal\n"
            "isolation: none\n"
            "---\n"
            "# Test Agent\n\n"
            "## Primary Objective\n\n"
            "Plan everything.\n\n"
            "## Execution Instructions\n\n"
            "1. Step one\n"
            "2. Step two\n\n"
            "## Memory & Entropy Constraints\n\n"
            "- Max 4096 tokens\n\n"
            "## Prohibited Actions\n\n"
            "- Never execute code\n"
        )
        defn = parse_agent_file(md)
        assert defn.name == "test_agent"
        assert defn.role == "planning"
        assert defn.model_routing["quality"] == "opus"
        assert "manual" in defn.triggers
        assert "temporal" in defn.triggers
        assert "Plan everything" in defn.primary_objective
        assert "Never execute code" in defn.prohibited_actions

    def test_missing_frontmatter_raises(self, tmp_path):
        md = tmp_path / "bad.md"
        md.write_text("# No frontmatter\nJust content.")
        with pytest.raises(ValueError, match="No valid YAML frontmatter"):
            parse_agent_file(md)

    def test_missing_name_raises(self, tmp_path):
        md = tmp_path / "noname.md"
        md.write_text("---\nrole: execution\n---\n# Agent\n")
        with pytest.raises(ValueError, match="missing 'name'"):
            parse_agent_file(md)


class TestParseSections:
    """Test markdown section extraction."""

    def test_extracts_sections(self):
        body = (
            "# Title\n\n"
            "## Section One\n\n"
            "Content one.\n\n"
            "## Section Two\n\n"
            "Content two.\n"
        )
        sections = _parse_sections(body)
        assert "section one" in sections
        assert "section two" in sections
        assert sections["section one"] == "Content one."

    def test_empty_body(self):
        sections = _parse_sections("")
        assert sections == {}


class TestLoadAllAgents:
    """Test loading agent definitions from the agents directory."""

    def test_loads_existing_agents(self):
        """Should find agent definitions in .agents/agents/."""
        agents = load_all_agents(force_reload=True)
        # We expect at least the 4 agents we created
        assert len(agents) >= 4
        assert "planner" in agents
        assert "executor" in agents
        assert "dream_subagent" in agents
        assert "reviewer" in agents

    def test_planner_has_correct_role(self):
        agents = load_all_agents(force_reload=True)
        assert agents["planner"].role == "planning"

    def test_executor_has_correct_role(self):
        agents = load_all_agents(force_reload=True)
        assert agents["executor"].role == "execution"

    def test_dream_subagent_has_full_isolation(self):
        agents = load_all_agents(force_reload=True)
        assert agents["dream_subagent"].isolation == "full"

    def test_reviewer_has_verification_role(self):
        agents = load_all_agents(force_reload=True)
        assert agents["reviewer"].role == "verification"

    def test_all_agents_have_model_routing(self):
        agents = load_all_agents(force_reload=True)
        for name, defn in agents.items():
            assert "quality" in defn.model_routing, (
                f"{name} missing quality routing"
            )
            assert "balanced" in defn.model_routing, (
                f"{name} missing balanced routing"
            )
            assert "budget" in defn.model_routing, (
                f"{name} missing budget routing"
            )

    def test_all_agents_have_prohibited_actions(self):
        agents = load_all_agents(force_reload=True)
        for name, defn in agents.items():
            assert len(defn.prohibited_actions) > 0, (
                f"{name} missing prohibited actions"
            )


class TestGetAgent:
    """Test single agent retrieval."""

    def test_existing_agent(self):
        defn = get_agent("planner", force_reload=True)
        assert defn is not None
        assert defn.name == "planner"

    def test_nonexistent_agent(self):
        defn = get_agent("nonexistent_agent_xyz", force_reload=True)
        assert defn is None
