# Multi-Agent Architecture

## Structure

- bin/lib: CommonJS core logic for the standalone motor (.cjs, require only)
- config: central runtime configuration (motor.json, environment overrides)
- agents: markdown definitions for planner, executor and specialists
- memory: live context index and archive snapshots (context.mmd, archive/)
- workflows: orchestration entry points (planning, execution, dream-cycle)
- docs: architecture and compliance reference

## Layering Model

- The backend follows the 13-layer model (L01-L13).
- Cross-layer communication goes through app.core.events.EventBus only.
- Layers may import shared, core, and config, but not other layers.
- New features must map to an existing layer; no ad-hoc layering.

## Agent Orchestration

- Planner creates a structured plan and writes it to memory/context.mmd.
- Executor reads the plan, implements tasks, and logs progress to memory.
- Dream Sub-Agent compresses and archives memory context on schedule.

## Integration Boundaries

- The standalone motor communicates with the backend only via /api/v1.
- Secrets and API keys are configured via environment variables only.
- No shell execution from backend code. Use allowed node/python APIs.
