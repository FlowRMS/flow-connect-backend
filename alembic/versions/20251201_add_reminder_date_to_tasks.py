"""add_reminder_date_to_tasks

Revision ID: a5e7c9d2b4f1
Revises: 9d142b0d8f38
Create Date: 2025-12-01 16:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5e7c9d2b4f1'
down_revision: str | None = '9d142b0d8f38'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add reminder_date column to tasks table
    op.add_column(
        'tasks',
        sa.Column('reminder_date', sa.Date(), nullable=True),
        schema='pycrm'
    )


def downgrade() -> None:
    # Remove reminder_date column from tasks table
    op.drop_column('tasks', 'reminder_date', schema='pycrm')
