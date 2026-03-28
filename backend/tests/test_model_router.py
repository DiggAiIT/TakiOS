"""Tests for the multi-model routing system."""

from app.core.ai.router import get_model_for_role, get_routing_table


class TestGetModelForRole:
    """Test model routing for different roles and profiles."""

    def test_quality_planning_uses_opus(self):
        model = get_model_for_role("planning", profile="quality")
        assert "opus" in model.lower()

    def test_quality_execution_uses_sonnet(self):
        model = get_model_for_role("execution", profile="quality")
        assert "sonnet" in model.lower()

    def test_quality_synthesis_uses_haiku(self):
        model = get_model_for_role("synthesis", profile="quality")
        assert "haiku" in model.lower()

    def test_quality_verification_uses_opus(self):
        model = get_model_for_role("verification", profile="quality")
        assert "opus" in model.lower()

    def test_balanced_planning_uses_opus(self):
        model = get_model_for_role("planning", profile="balanced")
        assert "opus" in model.lower()

    def test_balanced_execution_uses_sonnet(self):
        model = get_model_for_role("execution", profile="balanced")
        assert "sonnet" in model.lower()

    def test_balanced_verification_uses_sonnet(self):
        model = get_model_for_role("verification", profile="balanced")
        assert "sonnet" in model.lower()

    def test_budget_planning_uses_sonnet(self):
        model = get_model_for_role("planning", profile="budget")
        assert "sonnet" in model.lower()

    def test_budget_verification_uses_haiku(self):
        model = get_model_for_role("verification", profile="budget")
        assert "haiku" in model.lower()

    def test_inherit_returns_sonnet_default(self):
        model = get_model_for_role("planning", profile="inherit")
        assert "sonnet" in model.lower()

    def test_unknown_role_defaults_to_sonnet(self):
        model = get_model_for_role("unknown_role", profile="balanced")
        assert "sonnet" in model.lower()

    def test_unknown_profile_falls_back_to_balanced(self):
        model = get_model_for_role("planning", profile="nonexistent")
        assert "opus" in model.lower()

    def test_default_profile_from_settings(self):
        model = get_model_for_role("planning")
        assert model  # should resolve without error


class TestGetRoutingTable:
    """Test routing table generation."""

    def test_returns_all_profiles(self):
        table = get_routing_table()
        assert "quality" in table
        assert "balanced" in table
        assert "budget" in table

    def test_each_profile_has_all_roles(self):
        table = get_routing_table()
        for profile_name, role_map in table.items():
            assert "planning" in role_map
            assert "execution" in role_map
            assert "synthesis" in role_map
            assert "verification" in role_map

    def test_resolved_values_are_strings(self):
        table = get_routing_table()
        for role_map in table.values():
            for model_name in role_map.values():
                assert isinstance(model_name, str)
                assert len(model_name) > 0
