"""Dynamic multi-model routing for agent team operations.

Routes agent roles to appropriate model tiers based on the active
routing profile. Prevents premium model waste on routine tasks
and reserves high-tier reasoning for architectural decisions.
"""

from app.config import settings

# Model tier constants — resolved from settings at call time
_TIER_MAP = {
    "opus": lambda: settings.opus_model,
    "sonnet": lambda: settings.sonnet_model,
    "haiku": lambda: settings.haiku_model,
}

# Role-to-tier mapping per routing profile
_ROUTING_TABLE: dict[str, dict[str, str]] = {
    "quality": {
        "planning": "opus",
        "execution": "sonnet",
        "synthesis": "haiku",
        "verification": "opus",
    },
    "balanced": {
        "planning": "opus",
        "execution": "sonnet",
        "synthesis": "haiku",
        "verification": "sonnet",
    },
    "budget": {
        "planning": "sonnet",
        "execution": "sonnet",
        "synthesis": "haiku",
        "verification": "haiku",
    },
}


def get_model_for_role(role: str, profile: str | None = None) -> str:
    """Resolve the concrete model name for an agent role.

    Args:
        role: Agent operational role (planning, execution, synthesis, verification).
        profile: Routing profile override. If None, uses settings.model_routing_profile.

    Returns:
        Concrete model identifier string (e.g. "claude-opus-4-20250514").
    """
    active_profile = profile or settings.model_routing_profile

    if active_profile == "inherit":
        return settings.sonnet_model  # default to session model

    tier_map = _ROUTING_TABLE.get(active_profile, _ROUTING_TABLE["balanced"])
    tier = tier_map.get(role, "sonnet")
    resolver = _TIER_MAP.get(tier, _TIER_MAP["sonnet"])
    return resolver()


def get_routing_table() -> dict[str, dict[str, str]]:
    """Return the full routing table with resolved model names.

    Useful for API responses and debugging.
    """
    result: dict[str, dict[str, str]] = {}
    for profile_name, role_map in _ROUTING_TABLE.items():
        result[profile_name] = {}
        for role, tier in role_map.items():
            resolver = _TIER_MAP.get(tier, _TIER_MAP["sonnet"])
            result[profile_name][role] = resolver()
    return result
