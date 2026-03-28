"""Markdown agent definition parser.

Parses YAML frontmatter and structured sections from .agents/agents/*.md files.
Validates against the agent schema and caches parsed definitions.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AgentDefinition:
    """Parsed agent definition from a markdown file."""

    name: str
    model_routing: dict[str, str] = field(default_factory=dict)
    role: str = "execution"
    triggers: list[str] = field(default_factory=lambda: ["manual"])
    isolation: str = "none"
    primary_objective: str = ""
    execution_instructions: str = ""
    memory_constraints: str = ""
    prohibited_actions: str = ""
    raw_body: str = ""
    source_path: str = ""


# Simple YAML frontmatter regex: --- at start, content, --- delimiter
_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n(.*)",
    re.DOTALL,
)

# Section heading regex
_SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)

# Cache for parsed definitions
_cache: dict[str, AgentDefinition] = {}


def _parse_sections(body: str) -> dict[str, str]:
    """Extract ## sections from markdown body."""
    sections: dict[str, str] = {}
    parts = _SECTION_RE.split(body)
    # parts = [pre-heading, heading1, content1, heading2, content2, ...]
    for i in range(1, len(parts) - 1, 2):
        heading = parts[i].strip().lower()
        content = parts[i + 1].strip()
        sections[heading] = content
    return sections


def parse_agent_file(filepath: Path) -> AgentDefinition:
    """Parse a single agent definition markdown file.

    Args:
        filepath: Path to the .md file.

    Returns:
        Parsed AgentDefinition dataclass.

    Raises:
        ValueError: If file lacks valid frontmatter or required fields.
    """
    text = filepath.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"No valid YAML frontmatter found in {filepath}")

    frontmatter_str = match.group(1)
    body = match.group(2)

    frontmatter: dict[str, Any] = yaml.safe_load(frontmatter_str) or {}
    name = frontmatter.get("name")
    if not name:
        raise ValueError(f"Agent definition missing 'name' in {filepath}")

    # Parse triggers from comma-separated string
    triggers_raw = frontmatter.get("triggers", "manual")
    if isinstance(triggers_raw, str):
        triggers = [t.strip() for t in triggers_raw.split(",")]
    else:
        triggers = list(triggers_raw)

    sections = _parse_sections(body)

    return AgentDefinition(
        name=name,
        model_routing=frontmatter.get("model_routing", {}),
        role=frontmatter.get("role", "execution"),
        triggers=triggers,
        isolation=frontmatter.get("isolation", "none"),
        primary_objective=sections.get("primary objective", ""),
        execution_instructions=sections.get("execution instructions", ""),
        memory_constraints=sections.get("memory & entropy constraints", ""),
        prohibited_actions=sections.get("prohibited actions", ""),
        raw_body=body,
        source_path=str(filepath),
    )


def get_agents_dir() -> Path:
    """Resolve the .agents/agents/ directory relative to project root."""
    # Walk up from backend/app/services to find project root
    current = Path(__file__).resolve()
    for parent in current.parents:
        agents_dir = parent / ".agents" / "agents"
        if agents_dir.is_dir():
            return agents_dir
    # Fallback: assume standard project layout
    return Path(__file__).resolve().parent.parent.parent.parent / ".agents" / "agents"


def load_all_agents(force_reload: bool = False) -> dict[str, AgentDefinition]:
    """Load and cache all agent definitions from .agents/agents/.

    Args:
        force_reload: If True, clear cache and re-parse all files.

    Returns:
        Dict mapping agent name to AgentDefinition.
    """
    global _cache
    if _cache and not force_reload:
        return _cache

    _cache.clear()
    agents_dir = get_agents_dir()
    if not agents_dir.exists():
        return _cache

    for md_file in sorted(agents_dir.glob("*.md")):
        try:
            defn = parse_agent_file(md_file)
            _cache[defn.name] = defn
        except (ValueError, yaml.YAMLError):
            continue  # skip malformed files

    return _cache


def get_agent(name: str, force_reload: bool = False) -> AgentDefinition | None:
    """Get a single agent definition by name."""
    agents = load_all_agents(force_reload=force_reload)
    return agents.get(name)
