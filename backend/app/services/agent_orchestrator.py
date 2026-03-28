"""Central orchestrator for autonomous agent team operations.

Coordinates agent execution: loads definitions, determines model routing,
injects memory context, executes tasks, records outcomes, and publishes
completion events.
"""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.ai.client import get_ai_client
from app.core.ai.router import get_model_for_role
from app.core.events import EventBus
from app.core.memory.schemas import MemoryEntryCreate, MemorySessionCreate
from app.core.memory.service import MemoryService
from app.services.agent_parser import AgentDefinition, get_agent, load_all_agents


class AgentOrchestrator:
    """Coordinates multi-agent task execution with memory integration."""

    @staticmethod
    async def list_agents() -> list[dict]:
        """List all registered agent definitions."""
        agents = load_all_agents()
        return [
            {
                "name": defn.name,
                "role": defn.role,
                "triggers": defn.triggers,
                "isolation": defn.isolation,
                "model_routing": defn.model_routing,
                "primary_objective": defn.primary_objective[:200],
            }
            for defn in agents.values()
        ]

    @staticmethod
    async def run_agent(
        db: AsyncSession,
        agent_name: str,
        task: str,
        context: str = "",
    ) -> dict:
        """Execute an agent task with full memory lifecycle.

        Args:
            db: Active database session.
            agent_name: Name of the agent to invoke.
            task: Task description/instructions.
            context: Additional context to inject.

        Returns:
            Dict with execution result, metrics, and memory references.
        """
        # 1. Load agent definition
        defn = get_agent(agent_name)
        if defn is None:
            return {"error": f"Agent '{agent_name}' not found.", "status": "failed"}

        # 2. Create memory session
        mem_session = await MemoryService.create_session(
            db,
            MemorySessionCreate(
                agent_name=agent_name,
                task_summary=task[:2000],
            ),
        )

        # 3. Determine model via router
        model = get_model_for_role(defn.role)
        for profile, tier in defn.model_routing.items():
            if profile == settings.model_routing_profile:
                from app.core.ai.router import _TIER_MAP

                resolver = _TIER_MAP.get(tier, _TIER_MAP["sonnet"])
                model = resolver()
                break

        # 4. Build memory context
        index_rows = await MemoryService.get_memory_index(db)
        memory_context = "\n".join(
            f"- [{row.category}] {row.content}" for row in index_rows[:50]
        )

        # 5. Build prompt from agent definition + task
        system_prompt = (
            f"You are the '{defn.name}' agent.\n"
            f"Role: {defn.role}\n\n"
            f"## Objective\n{defn.primary_objective}\n\n"
            f"## Instructions\n{defn.execution_instructions}\n\n"
            f"## Constraints\n{defn.memory_constraints}\n\n"
            f"## Prohibited\n{defn.prohibited_actions}"
        )

        user_prompt = f"## Task\n{task}"
        if context:
            user_prompt += f"\n\n## Additional Context\n{context}"
        if memory_context:
            user_prompt += f"\n\n## Memory Index\n{memory_context}"

        # 6. Execute via AI client
        try:
            client = get_ai_client()
            result_text = await client.generate_text(
                prompt=user_prompt,
                system=system_prompt,
                max_tokens=8192,
                model=model,
            )
            status = "completed"
        except Exception as exc:
            result_text = f"Agent execution failed: {exc}"
            status = "failed"

        # 7. Record outcome to memory
        await MemoryService.record_entry(
            db,
            mem_session.id,
            MemoryEntryCreate(
                content=f"[{agent_name}] {status}: {task[:100]} -> {result_text[:200]}",
                category=defn.role,
            ),
        )

        # 8. Publish completion event
        await EventBus.publish(
            "agent_completed",
            {
                "agent_name": agent_name,
                "session_id": str(mem_session.id),
                "status": status,
                "role": defn.role,
            },
        )

        return {
            "status": status,
            "agent_name": agent_name,
            "model_used": model,
            "session_id": str(mem_session.id),
            "result": result_text,
            "token_estimate": max(1, len(result_text) // 4),
        }
