"""Add task_categories table and category_id to tasks

Revision ID: add_task_categories
Revises: takeoffs_product_crosses_001
Create Date: 2026-01-16

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_task_categories"
down_revision: str | None = "order_ack_m2m_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create task_categories table
    _ = op.create_table(
        "task_categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="pycrm",
    )

    # Create index on name for faster lookups
    op.create_index(
        "ix_task_categories_name",
        "task_categories",
        ["name"],
        schema="pycrm",
    )

    # Seed default categories
    op.execute("""
        INSERT INTO pycrm.task_categories (id, name, display_order) VALUES
        (gen_random_uuid(), 'Sales Call', 1),
        (gen_random_uuid(), 'Meeting', 2),
        (gen_random_uuid(), 'Follow-Up', 3),
        (gen_random_uuid(), 'Specification / Design Assist', 4),
        (gen_random_uuid(), 'Quoting', 5),
        (gen_random_uuid(), 'Order / Project Review', 6),
        (gen_random_uuid(), 'Distributor Engagement', 7),
        (gen_random_uuid(), 'Manufacturer Engagement', 8),
        (gen_random_uuid(), 'Training / Education', 9),
        (gen_random_uuid(), 'Event / Show', 10);
    """)

    # Add category_id column to tasks
    op.add_column(
        "tasks",
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema="pycrm",
    )

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_tasks_category_id",
        "tasks",
        "task_categories",
        ["category_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycrm",
        ondelete="SET NULL",
    )

    # Create index on category_id for faster joins
    op.create_index(
        "ix_tasks_category_id",
        "tasks",
        ["category_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    # Drop index on category_id
    op.drop_index("ix_tasks_category_id", table_name="tasks", schema="pycrm")

    # Drop foreign key constraint
    op.drop_constraint(
        "fk_tasks_category_id", "tasks", schema="pycrm", type_="foreignkey"
    )

    # Drop category_id column from tasks
    op.drop_column("tasks", "category_id", schema="pycrm")

    # Drop index on task_categories
    op.drop_index(
        "ix_task_categories_name", table_name="task_categories", schema="pycrm"
    )

    # Drop task_categories table
    op.drop_table("task_categories", schema="pycrm")
