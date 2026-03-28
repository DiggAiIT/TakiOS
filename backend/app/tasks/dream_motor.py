"""AutoDream background motor for memory consolidation.

Runs as an arq background task, triggered by temporal cron,
usage-based events, or manual API invocation. Strictly isolated
to memory data — never touches source code or configuration.

Compliance: EU AI Act Art. 12 (Traceability) — every dream cycle
is logged with timestamp, cycle number, metrics, and model info.
ISO/IEC 42001 — transparent risk documentation via structured logs.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.core.memory.compactor import MemoryCompactor
from app.core.memory.service import MemoryService
from app.database import async_session

logger = logging.getLogger("takios.dream")


def _load_dream_prompt() -> dict:
    """Load the dream synthesis prompt template."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "dream_prompt.json"
    if prompt_path.exists():
        with open(prompt_path) as f:
            return json.load(f)
    return {
        "system": "You are a memory compaction agent. Output only valid JSON.",
        "template": (
            "Consolidate memory entries into a compact index.\n"
            "Existing index:\n{existing_index}\n\n"
            "New entries:\n{new_entries}\n\n"
            "Rules:\n"
            "- Each line max 120 chars\n"
            "- Max {max_lines} total lines\n"
            "- Merge similar entries\n"
            "- Prune filler and redundancy\n"
            "- Output JSON array: [{{'content': '...', 'category': '...'}}]"
        ),
    }


async def async_dream_cycle(ctx: dict) -> dict:
    """Execute a dream cycle: load, compact, and rewrite the memory index.

    This is the core background motor. It:
    1. Loads unprocessed memory sessions from PostgreSQL.
    2. Gathers all active entries from those sessions.
    3. Loads the current compacted index.
    4. Runs the compactor (AI-assisted or local fallback).
    5. Replaces the index and marks sessions as processed.

    Returns:
        Dict with compaction metrics.
    """
    cycle_id = str(uuid.uuid4())
    cycle_start = datetime.now(timezone.utc)

    logger.info(
        "DREAM_CYCLE_START | cycle_id=%s timestamp=%s routing_profile=%s "
        "dream_interval_hours=%d session_threshold=%d max_index_lines=%d",
        cycle_id,
        cycle_start.isoformat(),
        settings.model_routing_profile,
        settings.dream_interval_hours,
        settings.dream_session_threshold,
        settings.max_index_lines,
    )

    async with async_session() as db:
        try:
            # 1. Get unprocessed sessions
            sessions = await MemoryService.get_unprocessed_sessions(db)
            if not sessions:
                logger.info(
                    "DREAM_CYCLE_SKIP | cycle_id=%s reason=no_unprocessed_sessions",
                    cycle_id,
                )
                return {
                    "status": "no_work",
                    "sessions_processed": 0,
                    "message": "No unprocessed sessions found.",
                }

            # 2. Gather entries from all unprocessed sessions
            all_entries: list[dict] = []
            all_entry_ids: list = []
            for mem_session in sessions:
                entries = await MemoryService.get_session_entries(db, mem_session.id)
                for entry in entries:
                    all_entries.append(
                        {
                            "id": str(entry.id),
                            "content": entry.content,
                            "category": entry.category,
                        }
                    )
                    all_entry_ids.append(entry.id)

            # 3. Load current index
            current_index_rows = await MemoryService.get_memory_index(db)
            existing_index = [
                {
                    "content": row.content,
                    "category": row.category,
                    "source_entry_ids": row.source_entry_ids,
                }
                for row in current_index_rows
            ]

            index_lines_before = len(existing_index)

            # 4. Determine dream cycle number
            current_cycle = max(
                (row.dream_cycle for row in current_index_rows), default=0
            ) + 1

            # 5. Run compaction
            dream_prompt = _load_dream_prompt()
            compactor = MemoryCompactor(use_ai=bool(settings.anthropic_api_key))

            try:
                new_index = await compactor.compact_entries_ai(
                    entries=all_entries,
                    existing_index=existing_index,
                    dream_prompt=dream_prompt,
                )
            except Exception:
                new_index = compactor.compact_entries_local(
                    entries=all_entries,
                    existing_index=existing_index,
                )

            # 6. Replace index
            lines_written = await MemoryService.replace_memory_index(
                db, new_index, current_cycle
            )

            # 7. Archive entries and mark sessions processed
            await MemoryService.archive_entries(db, all_entry_ids)
            session_ids = [s.id for s in sessions]
            await MemoryService.mark_sessions_processed(db, session_ids)

            await db.commit()

            cycle_end = datetime.now(timezone.utc)
            duration_ms = (cycle_end - cycle_start).total_seconds() * 1000
            token_estimate_before = sum(
                len(line.get("content", "")) // 4
                for line in existing_index
            )
            token_estimate_after = sum(
                len(line.get("content", "")) // 4
                for line in new_index
            )

            metrics = {
                "status": "completed",
                "cycle_id": cycle_id,
                "cycle_number": current_cycle,
                "sessions_processed": len(sessions),
                "entries_processed": len(all_entries),
                "entries_merged": len(all_entries),
                "index_lines_before": index_lines_before,
                "index_lines_after": lines_written,
                "token_estimate_saved": max(0, token_estimate_before - token_estimate_after),
                "duration_ms": round(duration_ms, 1),
            }

            # EU AI Act Art. 12 — Traceability log
            logger.info(
                "DREAM_CYCLE_COMPLETE | cycle_id=%s cycle_number=%d "
                "timestamp=%s duration_ms=%.1f "
                "sessions_processed=%d entries_processed=%d "
                "index_before=%d index_after=%d "
                "token_saved=%d model_profile=%s "
                "use_ai=%s",
                cycle_id,
                current_cycle,
                cycle_end.isoformat(),
                duration_ms,
                len(sessions),
                len(all_entries),
                index_lines_before,
                lines_written,
                metrics["token_estimate_saved"],
                settings.model_routing_profile,
                bool(settings.anthropic_api_key),
            )

            return metrics

        except Exception as exc:
            await db.rollback()
            logger.error(
                "DREAM_CYCLE_ERROR | cycle_id=%s timestamp=%s error=%s",
                cycle_id,
                datetime.now(timezone.utc).isoformat(),
                str(exc),
            )
            return {
                "status": "error",
                "cycle_id": cycle_id,
                "error": str(exc),
            }
