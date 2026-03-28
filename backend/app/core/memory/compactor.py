"""Memory compaction engine for the AutoDream cycle.

Merges redundant entries, prunes conversational filler,
and enforces the one-line-per-entry index format.
"""

import json
import re

from app.config import settings
from app.core.ai.client import get_ai_client
from app.core.ai.router import get_model_for_role


def _estimate_tokens(text: str) -> int:
    """Estimate token count (1 token ≈ 4 chars)."""
    return max(1, len(text) // 4)


FILLER_PATTERNS = [
    r"^(ok|okay|sure|got it|understood|alright|thanks|thank you)[.!,]?\s*$",
    r"^(let me|i will|i'll|going to)\s+(check|look|see|try)",
    r"^(here|this)\s+is\s+(the|a)\s+(result|output|answer)",
    r"^status:\s*(in.progress|started|beginning)",
]
_filler_re = re.compile("|".join(FILLER_PATTERNS), re.IGNORECASE)


def is_filler(text: str) -> bool:
    """Check if text is conversational filler that should be pruned."""
    stripped = text.strip()
    if len(stripped) < 10:
        return True
    return bool(_filler_re.match(stripped))


def truncate_to_line(text: str, max_chars: int = 120) -> str:
    """Truncate text to a single line within character limit."""
    line = text.replace("\n", " ").strip()
    if len(line) <= max_chars:
        return line
    return line[: max_chars - 3] + "..."


class MemoryCompactor:
    """Engine for compacting memory entries into index lines."""

    def __init__(self, use_ai: bool = True) -> None:
        self.use_ai = use_ai

    def compact_entries_local(
        self,
        entries: list[dict],
        existing_index: list[dict],
    ) -> list[dict]:
        """Compact entries using local heuristics (no AI call).

        Args:
            entries: List of dicts with 'id', 'content', 'category'.
            existing_index: Current index lines as dicts.

        Returns:
            New index lines as list of dicts.
        """
        # Start with existing index
        index_lines = list(existing_index)

        # Group new entries by category
        by_category: dict[str, list[dict]] = {}
        for entry in entries:
            if is_filler(entry.get("content", "")):
                continue
            cat = entry.get("category", "general")
            by_category.setdefault(cat, []).append(entry)

        # Merge entries within each category
        for category, cat_entries in by_category.items():
            merged_content = "; ".join(
                e["content"].replace("\n", " ").strip()
                for e in cat_entries
                if not is_filler(e.get("content", ""))
            )
            if not merged_content:
                continue

            compacted = truncate_to_line(merged_content)
            source_ids = ",".join(
                str(e.get("id", "")) for e in cat_entries
            )
            index_lines.append(
                {
                    "content": compacted,
                    "category": category,
                    "source_entry_ids": source_ids,
                }
            )

        # Enforce max lines by keeping most recent
        max_lines = settings.max_index_lines
        if len(index_lines) > max_lines:
            index_lines = index_lines[-max_lines:]

        return index_lines

    async def compact_entries_ai(
        self,
        entries: list[dict],
        existing_index: list[dict],
        dream_prompt: dict,
    ) -> list[dict]:
        """Compact entries using AI synthesis.

        Falls back to local compaction on AI failure.

        Args:
            entries: New memory entries to process.
            existing_index: Current index lines.
            dream_prompt: The dream prompt template with
                          'system' and 'template' keys.

        Returns:
            New index lines.
        """
        if not self.use_ai:
            return self.compact_entries_local(
                entries, existing_index
            )

        try:
            client = get_ai_client()
            model = get_model_for_role("synthesis")

            # Build prompt context
            existing_text = "\n".join(
                f"- [{line.get('category', 'general')}] "
                f"{line.get('content', '')}"
                for line in existing_index
            )
            new_entries_text = "\n".join(
                f"- [{e.get('category', 'general')}] "
                f"{e.get('content', '')}"
                for e in entries
                if not is_filler(e.get("content", ""))
            )

            prompt = dream_prompt.get("template", "").format(
                existing_index=existing_text,
                new_entries=new_entries_text,
                max_lines=settings.max_index_lines,
            )
            system = dream_prompt.get("system", "")

            response = await client.generate_text(
                prompt=prompt,
                system=system,
                max_tokens=2048,
                model=model,
            )

            # Parse JSON array response
            lines_data = json.loads(response)
            if not isinstance(lines_data, list):
                return self.compact_entries_local(
                    entries, existing_index
                )

            result = []
            for item in lines_data[: settings.max_index_lines]:
                if isinstance(item, dict):
                    result.append(
                        {
                            "content": truncate_to_line(
                                item.get("content", ""), 120
                            ),
                            "category": item.get(
                                "category", "general"
                            ),
                            "source_entry_ids": item.get(
                                "source_entry_ids", ""
                            ),
                        }
                    )
            return (
                result
                if result
                else self.compact_entries_local(
                    entries, existing_index
                )
            )

        except Exception:
            return self.compact_entries_local(
                entries, existing_index
            )
