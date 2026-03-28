"""Hierarchical memory system for autonomous agent teams.

Three-layer architecture:
- Active Layer: Redis-cached, session-scoped, ephemeral context.
- AutoMemory Layer: PostgreSQL-persistent operational records.
- AutoDream Layer: Compacted one-line index entries for long-term context.
"""
