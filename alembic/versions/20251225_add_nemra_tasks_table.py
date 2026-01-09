"""add nemra_tasks table

Revision ID: 74c4cd9e18c1
Revises: ea66509d1805
Create Date: 2025-12-25 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '74c4cd9e18c1'
down_revision: str | None = 'ea66509d1805'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        'nemra_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('added_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['page_id'], ['report.nemra_pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['report.nemra_modules.id'], ondelete='CASCADE'),
        schema='report'
    )
    
    op.create_index('ix_nemra_tasks_page_id', 'nemra_tasks', ['page_id'], schema='report')
    op.create_index('ix_nemra_tasks_module_id', 'nemra_tasks', ['module_id'], schema='report')
    op.create_index('ix_nemra_tasks_added_by', 'nemra_tasks', ['added_by'], schema='report')
    op.create_index('ix_nemra_tasks_assigned_to', 'nemra_tasks', ['assigned_to'], schema='report')
    op.create_index('ix_nemra_tasks_due_date', 'nemra_tasks', ['due_date'], schema='report')
    op.create_index('ix_nemra_tasks_created_at', 'nemra_tasks', ['created_at'], schema='report')


def downgrade() -> None:
    op.drop_index('ix_nemra_tasks_created_at', table_name='nemra_tasks', schema='report')
    op.drop_index('ix_nemra_tasks_due_date', table_name='nemra_tasks', schema='report')
    op.drop_index('ix_nemra_tasks_assigned_to', table_name='nemra_tasks', schema='report')
    op.drop_index('ix_nemra_tasks_added_by', table_name='nemra_tasks', schema='report')
    op.drop_index('ix_nemra_tasks_module_id', table_name='nemra_tasks', schema='report')
    op.drop_index('ix_nemra_tasks_page_id', table_name='nemra_tasks', schema='report')
    op.drop_table('nemra_tasks', schema='report')

