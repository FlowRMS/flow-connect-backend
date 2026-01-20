"""add nemra_notes_ai_summary table

Revision ID: 15c0cedaef19
Revises: 3fe635c98e32
Create Date: 2025-12-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "15c0cedaef19"
down_revision: str | None = "3fe635c98e32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "nemra_notes_ai_summary",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("summary_text", postgresql.JSONB(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("added_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema="report",
    )

    op.create_index(
        "ix_nemra_notes_ai_summary_created_at",
        "nemra_notes_ai_summary",
        [sa.text("created_at DESC")],
        schema="report",
    )
    op.create_index(
        "ix_nemra_notes_ai_summary_version",
        "nemra_notes_ai_summary",
        ["version"],
        schema="report",
    )
    op.create_index(
        "ix_nemra_notes_ai_summary_added_by",
        "nemra_notes_ai_summary",
        ["added_by"],
        schema="report",
    )
    op.create_index(
        "ix_nemra_notes_ai_summary_added_by_created_at",
        "nemra_notes_ai_summary",
        ["added_by", sa.text("created_at DESC")],
        schema="report",
    )
    op.create_index(
        "ix_nemra_notes_ai_summary_summary_text",
        "nemra_notes_ai_summary",
        ["summary_text"],
        schema="report",
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_nemra_notes_ai_summary_summary_text",
        table_name="nemra_notes_ai_summary",
        schema="report",
    )
    op.drop_index(
        "ix_nemra_notes_ai_summary_added_by_created_at",
        table_name="nemra_notes_ai_summary",
        schema="report",
    )
    op.drop_index(
        "ix_nemra_notes_ai_summary_added_by",
        table_name="nemra_notes_ai_summary",
        schema="report",
    )
    op.drop_index(
        "ix_nemra_notes_ai_summary_version",
        table_name="nemra_notes_ai_summary",
        schema="report",
    )
    op.drop_index(
        "ix_nemra_notes_ai_summary_created_at",
        table_name="nemra_notes_ai_summary",
        schema="report",
    )
    op.drop_table("nemra_notes_ai_summary", schema="report")
