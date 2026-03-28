#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

create_if_missing() {
  local target_path="$1"
  local content="$2"

  if [[ -e "$target_path" ]]; then
    printf 'skip %s\n' "$target_path"
    return 0
  fi

  printf '%s' "$content" > "$target_path"
  printf 'create %s\n' "$target_path"
}

mkdir -p \
  "$ROOT_DIR/bin/lib" \
  "$ROOT_DIR/agents" \
  "$ROOT_DIR/memory/archive" \
  "$ROOT_DIR/workflows" \
  "$ROOT_DIR/config" \
  "$ROOT_DIR/docs"

create_if_missing "$ROOT_DIR/bin/lib/motor.cjs" '"use strict";

const path = require("node:path");

const CONFIG_PATH = path.resolve(__dirname, "..", "..", "config", "motor.json");
const AGENTS_DIR = path.resolve(__dirname, "..", "..", "agents");
const MEMORY_DIR = path.resolve(__dirname, "..", "..", "memory");

function boot() {
  process.stdout.write(JSON.stringify({
    component: "motor.cjs",
    configPath: CONFIG_PATH,
    agentsDir: AGENTS_DIR,
    memoryDir: MEMORY_DIR,
    message: "Multi-agent motor scaffold ready"
  }) + "\n");
}

if (require.main === module) {
  boot();
}

module.exports = {
  boot,
  CONFIG_PATH,
  AGENTS_DIR,
  MEMORY_DIR,
};
'

create_if_missing "$ROOT_DIR/config/motor.json" '{
  "backendUrl": "http://localhost:8000",
  "apiPrefix": "/api/v1",
  "dreamIntervalMs": 43200000,
  "statusCheckIntervalMs": 300000,
  "sessionThreshold": 50,
  "maxIndexLines": 200,
  "maxLineChars": 120,
  "logLevel": "info"
}
'

create_if_missing "$ROOT_DIR/agents/planner.md" '---
name: planner
description: Plans tasks for the standalone multi-agent system.
model: opus
---

# Planner

- Role: break work into ordered, verifiable steps
- Output: structured plan entries for execution
- Constraints: respect architecture, compliance and logging rules
'

create_if_missing "$ROOT_DIR/agents/executor.md" '---
name: executor
description: Executes planned tasks for the standalone multi-agent system.
model: sonnet
---

# Executor

- Role: perform implementation tasks from the planner output
- Output: concrete changes, validation results and status updates
- Constraints: keep changes minimal, safe and testable
'

create_if_missing "$ROOT_DIR/agents/dream_subagent.md" '---
name: dream_subagent
description: Compresses and maintains memory context for the standalone multi-agent system.
model: haiku
---

# Dream Sub-Agent

- Role: condense memory and archive older context
- Output: compact entries for memory/context.mmd
- Constraints: keep entries short, structured and traceable
'

create_if_missing "$ROOT_DIR/agents/mechanism-agent.md" '---
name: mechanism-agent
description: Specialized agent for mechanism and orchestration analysis.
model: sonnet
---

# Mechanism Agent

- Role: inspect system behavior and orchestration details
- Output: mechanism-focused findings and recommendations
- Constraints: align with core architecture and backend API boundaries
'

create_if_missing "$ROOT_DIR/memory/context.mmd" '# Memory Context Index
# Maintained by the Dream Sub-Agent
# Format: [CATEGORY] Compressed content
# Last cycle: none
'

create_if_missing "$ROOT_DIR/memory/archive/.gitkeep" ''

create_if_missing "$ROOT_DIR/workflows/planning.yml" 'name: planning

on:
  workflow_dispatch:

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - name: Placeholder planning workflow
        run: echo "planning workflow scaffold"
'

create_if_missing "$ROOT_DIR/workflows/execution.yml" 'name: execution

on:
  workflow_dispatch:

jobs:
  execute:
    runs-on: ubuntu-latest
    steps:
      - name: Placeholder execution workflow
        run: echo "execution workflow scaffold"
'

create_if_missing "$ROOT_DIR/workflows/dream-cycle.yml" 'name: dream-cycle

on:
  workflow_dispatch:

jobs:
  dream:
    runs-on: ubuntu-latest
    steps:
      - name: Placeholder dream workflow
        run: echo "dream cycle workflow scaffold"
'

create_if_missing "$ROOT_DIR/docs/ARCHITECTURE.md" '# Multi-Agent Architecture

- bin/lib: CommonJS core logic for the standalone motor
- config: central runtime configuration
- agents: markdown definitions for planner, executor and specialists
- memory: live context and archived context snapshots
- workflows: orchestration entry points
'

create_if_missing "$ROOT_DIR/docs/COMPLIANCE.md" '# Compliance Notes

- Log AI-relevant decisions with UTC timestamps and request identifiers
- Keep secrets in environment variables only
- Communicate with the backend through the REST API under /api/v1
'

printf 'Scaffold complete in %s\n' "$ROOT_DIR"