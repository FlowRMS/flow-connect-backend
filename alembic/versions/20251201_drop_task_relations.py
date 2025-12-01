"""drop_task_relations

Revision ID: 9d142b0d8f38
Revises: 8c031a9c7e27
Create Date: 2025-12-01 15:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9d142b0d8f38'
down_revision: str | None = '8c031a9c7e27'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop index and table for task_relations (replaced by link_relations)
    op.drop_index('ix_crm_task_relations_task_id_related_type_related_id', table_name='task_relations', schema='crm')
    op.drop_table('task_relations', schema='crm')


def downgrade() -> None:
    # Recreate task_relations table
    _ = op.create_table(
        'task_relations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('related_type', sa.SmallInteger(), nullable=False),
        sa.Column('related_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['crm.tasks.id'], name='fk_task_relations_task_id'),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Recreate index
    op.create_index(
        'ix_crm_task_relations_task_id_related_type_related_id',
        'task_relations',
        ['task_id', 'related_type', 'related_id'],
        schema='crm'
    )
