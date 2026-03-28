# Agent Definition Schema

All agents in the `.agents/agents/` directory follow this standardized schema.

## YAML Frontmatter

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `name` | string | yes | — | Unique agent identifier (lowercase, no spaces) |
| `model_routing` | object | yes | — | Model tier per routing profile |
| `model_routing.quality` | string | yes | `opus`, `sonnet`, `haiku` | Model for quality profile |
| `model_routing.balanced` | string | yes | `opus`, `sonnet`, `haiku` | Model for balanced profile |
| `model_routing.budget` | string | yes | `opus`, `sonnet`, `haiku` | Model for budget profile |
| `role` | string | yes | `planning`, `execution`, `synthesis`, `verification` | Agent's operational role |
| `triggers` | string | yes | comma-separated: `manual`, `temporal`, `usage` | Activation mechanisms |
| `isolation` | string | yes | `full`, `memory_only`, `none` | Isolation level from active session |

## Markdown Body Sections

| Section | Required | Purpose |
|---------|----------|---------|
| `# <Agent Name>` | yes | H1 title matching the agent's display name |
| `## Primary Objective` | yes | Single-paragraph mission statement |
| `## Execution Instructions` | yes | Numbered step-by-step operational procedure |
| `## Memory & Entropy Constraints` | yes | Token budgets, memory access permissions, entropy rules |
| `## Prohibited Actions` | yes | Explicit list of forbidden operations |

## Placeholder Convention

Use `<PLACEHOLDER_*>` tags for all project-specific values:

| Placeholder | Description | Example Value |
|-------------|-------------|---------------|
| `<PLACEHOLDER_PROJECT_SOURCE_PATH>` | Root path of project source code | `backend/app/` |
| `<PLACEHOLDER_MEMORY_INDEX_PATH>` | Path to compacted memory index | `memory/index.mmd` |
| `<PLACEHOLDER_MEMORY_AUTOMEMORY_PATH>` | Path to AutoMemory storage | `memory/sessions/` |
| `<PLACEHOLDER_DREAM_INTERVAL_HOURS>` | Hours between automatic dream cycles | `12` |
| `<PLACEHOLDER_DREAM_SESSION_THRESHOLD>` | Session count triggering dream cycle | `50` |
| `<PLACEHOLDER_MAX_INDEX_LINES>` | Maximum lines in compacted index | `200` |

## Routing Profiles

| Profile | Planning | Execution | Synthesis | Verification |
|---------|----------|-----------|-----------|--------------|
| **quality** | Opus | Sonnet | Haiku | Opus |
| **balanced** | Opus | Sonnet | Haiku | Sonnet |
| **budget** | Sonnet | Sonnet | Haiku | Haiku |
| **inherit** | Session model | Session model | Session model | Session model |
