"""Add task_assignees table for multiple assignees

Revision ID: add_task_assignees
Revises: add_visible_to_users
Create Date: 2026-01-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_task_assignees"
down_revision: str | None = "add_visible_to_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "task_assignees",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), nullable=False, primary_key=True
        ),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["task_id"], ["pycrm.tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["pyuser.users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("task_id", "user_id", name="uq_task_assignees_task_user"),
        schema="pycrm",
    )
    op.create_index(
        "ix_task_assignees_task_id",
        "task_assignees",
        ["task_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_task_assignees_user_id",
        "task_assignees",
        ["user_id"],
        schema="pycrm",
    )

    # Migrate existing assigned_to_id data to new table
    op.execute("""
        INSERT INTO pycrm.task_assignees (id, task_id, user_id, created_at)
        SELECT
            gen_random_uuid(),
            id,
            assigned_to_id,
            now()
        FROM pycrm.tasks
        WHERE assigned_to_id IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_index(
        "ix_task_assignees_user_id", table_name="task_assignees", schema="pycrm"
    )
    op.drop_index(
        "ix_task_assignees_task_id", table_name="task_assignees", schema="pycrm"
    )
    op.drop_table("task_assignees", schema="pycrm")
