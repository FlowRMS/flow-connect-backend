"""add nemra_discussions table

Revision ID: e0a5448589d9
Revises: 74c4cd9e18c1
Create Date: 2025-12-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e0a5448589d9"
down_revision: str | None = "74c4cd9e18c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "nemra_discussions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("discussion_detail", sa.Text(), nullable=False),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["page_id"], ["report.nemra_pages.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["module_id"], ["report.nemra_modules.id"], ondelete="CASCADE"
        ),
        schema="report",
    )

    op.create_index(
        "ix_nemra_discussions_page_id",
        "nemra_discussions",
        ["page_id"],
        schema="report",
    )
    op.create_index(
        "ix_nemra_discussions_module_id",
        "nemra_discussions",
        ["module_id"],
        schema="report",
    )
    op.create_index(
        "ix_nemra_discussions_added_by",
        "nemra_discussions",
        ["added_by"],
        schema="report",
    )
    op.create_index(
        "ix_nemra_discussions_created_at",
        "nemra_discussions",
        ["created_at"],
        schema="report",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_nemra_discussions_created_at",
        table_name="nemra_discussions",
        schema="report",
    )
    op.drop_index(
        "ix_nemra_discussions_added_by", table_name="nemra_discussions", schema="report"
    )
    op.drop_index(
        "ix_nemra_discussions_module_id",
        table_name="nemra_discussions",
        schema="report",
    )
    op.drop_index(
        "ix_nemra_discussions_page_id", table_name="nemra_discussions", schema="report"
    )
    op.drop_table("nemra_discussions", schema="report")
