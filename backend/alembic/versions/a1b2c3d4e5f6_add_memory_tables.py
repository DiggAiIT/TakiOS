"""Add memory tables for agent team system.

Revision ID: a1b2c3d4e5f6
Revises: cd4b5f442600
Create Date: 2026-03-27 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "cd4b5f442600"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "memory_session",
        sa.Column("id", sa.Uuid(), nullable=False, primary_key=True),
        sa.Column("agent_name", sa.String(100), nullable=False, index=True),
        sa.Column("task_summary", sa.Text(), server_default=""),
        sa.Column("turn_count", sa.Integer(), server_default="0"),
        sa.Column("token_estimate", sa.Integer(), server_default="0"),
        sa.Column("is_dream_processed", sa.Boolean(), server_default="false", index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "memory_entry",
        sa.Column("id", sa.Uuid(), nullable=False, primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("memory_session.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "layer",
            sa.Enum("active", "automemory", "autodream", name="memorylayer"),
            nullable=False,
            server_default="automemory",
            index=True,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "archived", "pruned", name="memoryentrystatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("compacted_line", sa.String(120), nullable=True),
        sa.Column("category", sa.String(50), server_default="general", index=True),
        sa.Column("token_estimate", sa.Integer(), server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "memory_index",
        sa.Column("id", sa.Uuid(), nullable=False, primary_key=True),
        sa.Column("line_number", sa.Integer(), nullable=False, index=True),
        sa.Column("content", sa.String(120), nullable=False),
        sa.Column("category", sa.String(50), server_default="general", index=True),
        sa.Column("source_entry_ids", sa.Text(), server_default=""),
        sa.Column("dream_cycle", sa.Integer(), server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("memory_index")
    op.drop_table("memory_entry")
    op.drop_table("memory_session")
    sa.Enum("active", "automemory", "autodream", name="memorylayer").drop(
        op.get_bind(), checkfirst=True
    )
    sa.Enum("active", "archived", "pruned", name="memoryentrystatus").drop(
        op.get_bind(), checkfirst=True
    )
