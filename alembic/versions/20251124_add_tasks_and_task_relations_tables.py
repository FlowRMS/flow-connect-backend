"""add tasks and task_relations tables

Revision ID: a1b2c3d4e5f6
Revises: 87005d4e17a7
Create Date: 2025-11-24 20:58:19

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "87005d4e17a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create tasks table
    _ = op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False),
        sa.Column("priority", sa.SmallInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="crm",
    )

    # Create indexes for tasks table
    op.create_index(
        "ix_crm_tasks_assigned_to_id", "tasks", ["assigned_to_id"], schema="crm"
    )
    op.create_index("ix_crm_tasks_created_by", "tasks", ["created_by"], schema="crm")
    op.create_index("ix_crm_tasks_due_date", "tasks", ["due_date"], schema="crm")
    op.create_index("ix_crm_tasks_status", "tasks", ["status"], schema="crm")

    # Create task_relations table
    _ = op.create_table(
        "task_relations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("related_type", sa.SmallInteger(), nullable=False),
        sa.Column("related_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["crm.tasks.id"],
            name="fk_task_relations_task_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="crm",
    )

    # Create composite index for task_relations
    op.create_index(
        "ix_crm_task_relations_task_id_related_type_related_id",
        "task_relations",
        ["task_id", "related_type", "related_id"],
        schema="crm",
    )


def downgrade() -> None:
    # Drop task_relations table and its indexes
    op.drop_index(
        "ix_crm_task_relations_task_id_related_type_related_id",
        table_name="task_relations",
        schema="crm",
    )
    op.drop_table("task_relations", schema="crm")

    # Drop tasks table and its indexes
    op.drop_index("ix_crm_tasks_status", table_name="tasks", schema="crm")
    op.drop_index("ix_crm_tasks_due_date", table_name="tasks", schema="crm")
    op.drop_index("ix_crm_tasks_created_by", table_name="tasks", schema="crm")
    op.drop_index("ix_crm_tasks_assigned_to_id", table_name="tasks", schema="crm")
    op.drop_table("tasks", schema="crm")
