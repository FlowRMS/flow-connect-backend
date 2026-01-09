"""add nemra_notes table

Revision ID: ea66509d1805
Revises: dce57ae2783a
Create Date: 2025-12-25 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'ea66509d1805'
down_revision: str | None = 'dce57ae2783a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        'nemra_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('note_detail', sa.Text(), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('added_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['page_id'], ['report.nemra_pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['report.nemra_modules.id'], ondelete='CASCADE'),
        schema='report'
    )
    
    op.create_index('ix_nemra_notes_page_id', 'nemra_notes', ['page_id'], schema='report')
    op.create_index('ix_nemra_notes_module_id', 'nemra_notes', ['module_id'], schema='report')
    op.create_index('ix_nemra_notes_added_by', 'nemra_notes', ['added_by'], schema='report')
    op.create_index('ix_nemra_notes_created_at', 'nemra_notes', ['created_at'], schema='report')


def downgrade() -> None:
    op.drop_index('ix_nemra_notes_created_at', table_name='nemra_notes', schema='report')
    op.drop_index('ix_nemra_notes_added_by', table_name='nemra_notes', schema='report')
    op.drop_index('ix_nemra_notes_module_id', table_name='nemra_notes', schema='report')
    op.drop_index('ix_nemra_notes_page_id', table_name='nemra_notes', schema='report')
    op.drop_table('nemra_notes', schema='report')

