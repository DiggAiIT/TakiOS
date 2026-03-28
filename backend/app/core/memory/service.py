"""Three-layer memory service for autonomous agent teams.

Layers:
- Active: Redis-cached ephemeral session context.
- AutoMemory: PostgreSQL-persistent operational records.
- AutoDream: Compacted index maintained by the Dream Sub-agent.
"""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.events import EventBus
from app.core.memory.models import (
    MemoryEntry,
    MemoryEntryStatus,
    MemoryIndex,
    MemoryLayer,
    MemorySession,
)
from app.core.memory.schemas import (
    DreamCycleResponse,
    MemoryEntryCreate,
    MemoryIndexResponse,
    MemorySessionCreate,
    MemoryStatusResponse,
)


def _estimate_tokens(text: str) -> int:
    """Estimate token count using character heuristic (1 token ≈ 4 chars)."""
    return max(1, len(text) // 4)


class MemoryService:
    """Central service for the three-layer hierarchical memory system."""

    # ── Active Layer (Redis) ──────────────────────────────────────────

    @staticmethod
    async def set_active_context(
        session_id: str, key: str, value: str
    ) -> None:
        """Store ephemeral context in Redis for the active session."""
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url)
        try:
            redis_key = f"memory:active:{session_id}:{key}"
            await r.set(redis_key, value, ex=3600)  # 1h TTL
        finally:
            await r.aclose()

    @staticmethod
    async def get_active_context(
        session_id: str, key: str
    ) -> str | None:
        """Retrieve ephemeral context from Redis."""
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url)
        try:
            redis_key = f"memory:active:{session_id}:{key}"
            val = await r.get(redis_key)
            return val.decode() if val else None
        finally:
            await r.aclose()

    @staticmethod
    async def clear_active_context(session_id: str) -> int:
        """Clear all active context for a session. Returns keys deleted."""
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url)
        try:
            pattern = f"memory:active:{session_id}:*"
            keys = []
            async for key in r.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await r.delete(*keys)
            return 0
        finally:
            await r.aclose()

    # ── AutoMemory Layer (PostgreSQL) ─────────────────────────────────

    @staticmethod
    async def create_session(
        db: AsyncSession, data: MemorySessionCreate
    ) -> MemorySession:
        """Create a new memory session for an agent interaction."""
        session = MemorySession(
            agent_name=data.agent_name,
            task_summary=data.task_summary,
        )
        db.add(session)
        await db.flush()
        return session

    @staticmethod
    async def record_entry(
        db: AsyncSession,
        session_id: uuid.UUID,
        data: MemoryEntryCreate,
    ) -> MemoryEntry:
        """Record a memory entry in the AutoMemory layer."""
        token_est = _estimate_tokens(data.content)
        entry = MemoryEntry(
            session_id=session_id,
            layer=MemoryLayer.automemory,
            content=data.content,
            category=data.category,
            token_estimate=token_est,
        )
        db.add(entry)
        await db.flush()

        # Update session counters
        stmt = select(MemorySession).where(
            MemorySession.id == session_id
        )
        result = await db.execute(stmt)
        mem_session = result.scalar_one_or_none()
        if mem_session:
            mem_session.turn_count += 1
            mem_session.token_estimate += token_est

            # Check usage-based dream trigger
            threshold = settings.dream_session_threshold
            if (
                mem_session.turn_count >= threshold
                and not mem_session.is_dream_processed
            ):
                await EventBus.publish(
                    "dream_trigger_usage",
                    {
                        "session_id": str(session_id),
                        "turn_count": mem_session.turn_count,
                    },
                )

        return entry

    @staticmethod
    async def get_unprocessed_sessions(
        db: AsyncSession,
    ) -> list[MemorySession]:
        """Get all sessions not yet processed by the Dream Sub-agent."""
        stmt = (
            select(MemorySession)
            .where(MemorySession.is_dream_processed.is_(False))
            .order_by(MemorySession.created_at)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_session_entries(
        db: AsyncSession, session_id: uuid.UUID
    ) -> list[MemoryEntry]:
        """Get all active entries for a session."""
        stmt = (
            select(MemoryEntry)
            .where(
                MemoryEntry.session_id == session_id,
                MemoryEntry.status == MemoryEntryStatus.active,
            )
            .order_by(MemoryEntry.created_at)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ── AutoDream Layer (Compacted Index) ─────────────────────────────

    @staticmethod
    async def get_memory_index(
        db: AsyncSession,
    ) -> list[MemoryIndex]:
        """Retrieve the full compacted memory index."""
        stmt = select(MemoryIndex).order_by(MemoryIndex.line_number)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def replace_memory_index(
        db: AsyncSession,
        lines: list[dict],
        dream_cycle: int,
    ) -> int:
        """Replace the entire memory index with new compacted lines.

        Args:
            db: Database session.
            lines: List of dicts with 'content', 'category',
                   'source_entry_ids'.
            dream_cycle: Current dream cycle number.

        Returns:
            Number of index lines written.
        """
        # Delete existing index
        existing = await db.execute(select(MemoryIndex))
        for row in existing.scalars().all():
            await db.delete(row)
        await db.flush()

        # Write new index
        max_lines = settings.max_index_lines
        for i, line_data in enumerate(lines[:max_lines]):
            content = line_data.get("content", "")[:120]
            idx = MemoryIndex(
                line_number=i,
                content=content,
                category=line_data.get("category", "general"),
                source_entry_ids=line_data.get(
                    "source_entry_ids", ""
                ),
                dream_cycle=dream_cycle,
            )
            db.add(idx)

        await db.flush()
        return min(len(lines), max_lines)

    @staticmethod
    async def mark_sessions_processed(
        db: AsyncSession, session_ids: list[uuid.UUID]
    ) -> None:
        """Mark sessions as processed by the Dream Sub-agent."""
        if not session_ids:
            return
        stmt = select(MemorySession).where(
            MemorySession.id.in_(session_ids)
        )
        result = await db.execute(stmt)
        for session in result.scalars().all():
            session.is_dream_processed = True
        await db.flush()

    @staticmethod
    async def archive_entries(
        db: AsyncSession, entry_ids: list[uuid.UUID]
    ) -> None:
        """Archive memory entries after dream processing."""
        if not entry_ids:
            return
        stmt = select(MemoryEntry).where(
            MemoryEntry.id.in_(entry_ids)
        )
        result = await db.execute(stmt)
        for entry in result.scalars().all():
            entry.status = MemoryEntryStatus.archived
        await db.flush()

    # ── Status & Metrics ──────────────────────────────────────────────

    @staticmethod
    async def get_status(db: AsyncSession) -> MemoryStatusResponse:
        """Get memory system status overview."""
        active_sessions = await db.scalar(
            select(func.count()).select_from(MemorySession)
        )
        total_entries = await db.scalar(
            select(func.count()).select_from(MemoryEntry)
        )
        unprocessed = await db.scalar(
            select(func.count())
            .select_from(MemorySession)
            .where(MemorySession.is_dream_processed.is_(False))
        )
        index_lines = await db.scalar(
            select(func.count()).select_from(MemoryIndex)
        )
        last_dream = await db.scalar(
            select(func.max(MemoryIndex.created_at))
        )
        max_cycle = await db.scalar(
            select(func.max(MemoryIndex.dream_cycle))
        )

        return MemoryStatusResponse(
            active_sessions=active_sessions or 0,
            total_entries=total_entries or 0,
            unprocessed_sessions=unprocessed or 0,
            index_lines=index_lines or 0,
            max_index_lines=settings.max_index_lines,
            last_dream_cycle=last_dream,
            total_dream_cycles=max_cycle or 0,
        )
