"""add strategic_ask and strategic_ask_responses tables

Revision ID: 3fe635c98e32
Revises: 724a9b95cf93
Create Date: 2025-12-25 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '3fe635c98e32'
down_revision: str | None = '724a9b95cf93'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        'strategic_ask',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_text', sa.Text(), nullable=False),
        sa.Column('added_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['page_id'], ['report.nemra_pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['report.nemra_modules.id'], ondelete='CASCADE'),
        schema='report'
    )
    
    op.create_index('ix_strategic_ask_page_id', 'strategic_ask', ['page_id'], schema='report')
    op.create_index('ix_strategic_ask_module_id', 'strategic_ask', ['module_id'], schema='report')
    op.create_index('ix_strategic_ask_added_by', 'strategic_ask', ['added_by'], schema='report')
    op.create_index('ix_strategic_ask_created_at', 'strategic_ask', ['created_at'], schema='report')
    
    _ = op.create_table(
        'strategic_ask_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('strategic_ask_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(255), nullable=False),
        sa.Column('priority', sa.String(50), nullable=False),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('eta', sa.String(255), nullable=True),
        sa.Column('added_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['strategic_ask_id'], ['report.strategic_ask.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['page_id'], ['report.nemra_pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['report.nemra_modules.id'], ondelete='CASCADE'),
        schema='report'
    )
    
    op.create_index('ix_strategic_ask_responses_strategic_ask_id', 'strategic_ask_responses', ['strategic_ask_id'], schema='report')
    op.create_index('ix_strategic_ask_responses_page_id', 'strategic_ask_responses', ['page_id'], schema='report')
    op.create_index('ix_strategic_ask_responses_module_id', 'strategic_ask_responses', ['module_id'], schema='report')
    op.create_index('ix_strategic_ask_responses_added_by', 'strategic_ask_responses', ['added_by'], schema='report')
    op.create_index('ix_strategic_ask_responses_created_at', 'strategic_ask_responses', ['created_at'], schema='report')
    op.create_index('ix_strategic_ask_responses_priority', 'strategic_ask_responses', ['priority'], schema='report')
    op.create_index('ix_strategic_ask_responses_category', 'strategic_ask_responses', ['category'], schema='report')


def downgrade() -> None:
    op.drop_index('ix_strategic_ask_responses_category', table_name='strategic_ask_responses', schema='report')
    op.drop_index('ix_strategic_ask_responses_priority', table_name='strategic_ask_responses', schema='report')
    op.drop_index('ix_strategic_ask_responses_created_at', table_name='strategic_ask_responses', schema='report')
    op.drop_index('ix_strategic_ask_responses_added_by', table_name='strategic_ask_responses', schema='report')
    op.drop_index('ix_strategic_ask_responses_module_id', table_name='strategic_ask_responses', schema='report')
    op.drop_index('ix_strategic_ask_responses_page_id', table_name='strategic_ask_responses', schema='report')
    op.drop_index('ix_strategic_ask_responses_strategic_ask_id', table_name='strategic_ask_responses', schema='report')
    op.drop_table('strategic_ask_responses', schema='report')
    
    op.drop_index('ix_strategic_ask_created_at', table_name='strategic_ask', schema='report')
    op.drop_index('ix_strategic_ask_added_by', table_name='strategic_ask', schema='report')
    op.drop_index('ix_strategic_ask_module_id', table_name='strategic_ask', schema='report')
    op.drop_index('ix_strategic_ask_page_id', table_name='strategic_ask', schema='report')
    op.drop_table('strategic_ask', schema='report')

