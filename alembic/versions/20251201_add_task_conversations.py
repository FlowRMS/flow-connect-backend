"""add_task_conversations

Revision ID: 8c031a9c7e27
Revises: 0b3a96d1edc3
Create Date: 2025-12-01 13:53:55.366074

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8c031a9c7e27'
down_revision: str | None = '0b3a96d1edc3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create task_conversations table
    _ = op.create_table(
        'task_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['pycrm.tasks.id'], name='fk_task_conversations_task_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='pycrm'
    )

    # Create index on task_conversations for efficient lookups
    op.create_index(
        'ix_crm_task_conversations_task_id',
        'task_conversations',
        ['task_id'],
        schema='pycrm'
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_crm_task_conversations_task_id', table_name='task_conversations', schema='pycrm')
    op.drop_table('task_conversations', schema='pycrm')
