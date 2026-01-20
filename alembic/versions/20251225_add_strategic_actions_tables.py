"""add strategic_actions and strategic_action_responses tables

Revision ID: 724a9b95cf93
Revises: e0a5448589d9
Create Date: 2025-12-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "724a9b95cf93"
down_revision: str | None = "e0a5448589d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "strategic_actions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_text", sa.Text(), nullable=False),
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
        "ix_strategic_actions_page_id",
        "strategic_actions",
        ["page_id"],
        schema="report",
    )
    op.create_index(
        "ix_strategic_actions_module_id",
        "strategic_actions",
        ["module_id"],
        schema="report",
    )
    op.create_index(
        "ix_strategic_actions_added_by",
        "strategic_actions",
        ["added_by"],
        schema="report",
    )
    op.create_index(
        "ix_strategic_actions_created_at",
        "strategic_actions",
        ["created_at"],
        schema="report",
    )

    _ = op.create_table(
        "strategic_action_responses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("strategic_action_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("impact", sa.Text(), nullable=False),
        sa.Column("timeline", sa.Text(), nullable=False),
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
            ["strategic_action_id"], ["report.strategic_actions.id"], ondelete="CASCADE"
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
        "ix_strategic_action_responses_strategic_action_id",
        "strategic_action_responses",
        ["strategic_action_id"],
        schema="report",
    )
    op.create_index(
        "ix_strategic_action_responses_page_id",
        "strategic_action_responses",
        ["page_id"],
        schema="report",
    )
    op.create_index(
        "ix_strategic_action_responses_module_id",
        "strategic_action_responses",
        ["module_id"],
        schema="report",
    )
    op.create_index(
        "ix_strategic_action_responses_added_by",
        "strategic_action_responses",
        ["added_by"],
        schema="report",
    )
    op.create_index(
        "ix_strategic_action_responses_created_at",
        "strategic_action_responses",
        ["created_at"],
        schema="report",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_strategic_action_responses_created_at",
        table_name="strategic_action_responses",
        schema="report",
    )
    op.drop_index(
        "ix_strategic_action_responses_added_by",
        table_name="strategic_action_responses",
        schema="report",
    )
    op.drop_index(
        "ix_strategic_action_responses_module_id",
        table_name="strategic_action_responses",
        schema="report",
    )
    op.drop_index(
        "ix_strategic_action_responses_page_id",
        table_name="strategic_action_responses",
        schema="report",
    )
    op.drop_index(
        "ix_strategic_action_responses_strategic_action_id",
        table_name="strategic_action_responses",
        schema="report",
    )
    op.drop_table("strategic_action_responses", schema="report")

    op.drop_index(
        "ix_strategic_actions_created_at",
        table_name="strategic_actions",
        schema="report",
    )
    op.drop_index(
        "ix_strategic_actions_added_by", table_name="strategic_actions", schema="report"
    )
    op.drop_index(
        "ix_strategic_actions_module_id",
        table_name="strategic_actions",
        schema="report",
    )
    op.drop_index(
        "ix_strategic_actions_page_id", table_name="strategic_actions", schema="report"
    )
    op.drop_table("strategic_actions", schema="report")
