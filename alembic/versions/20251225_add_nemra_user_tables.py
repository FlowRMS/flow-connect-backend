"""add nemra_user_folders, nemra_user_templates, nemra_user_pages, nemra_user_modules tables

Revision ID: 23c443a27ef7
Revises: 9159d757c059
Create Date: 2025-12-25 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '23c443a27ef7'
down_revision: str | None = '9159d757c059'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        'nemra_user_folders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nemra_folder_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['nemra_folder_id'], ['report.nemra_folders.id'], ondelete='SET NULL'),
        schema='report'
    )
    
    op.create_index('ix_nemra_user_folders_nemra_folder_id', 'nemra_user_folders', ['nemra_folder_id'], schema='report')
    op.create_index('ix_nemra_user_folders_user_id', 'nemra_user_folders', ['user_id'], schema='report')
    op.create_index('ix_nemra_user_folders_created_at', 'nemra_user_folders', ['created_at'], schema='report')
    
    _ = op.create_table(
        'nemra_user_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nemra_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('nemra_user_folder_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['nemra_template_id'], ['report.nemra_templates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['nemra_user_folder_id'], ['report.nemra_user_folders.id'], ondelete='SET NULL'),
        schema='report'
    )
    
    op.create_index('ix_nemra_user_templates_nemra_template_id', 'nemra_user_templates', ['nemra_template_id'], schema='report')
    op.create_index('ix_nemra_user_templates_nemra_user_folder_id', 'nemra_user_templates', ['nemra_user_folder_id'], schema='report')
    op.create_index('ix_nemra_user_templates_user_id', 'nemra_user_templates', ['user_id'], schema='report')
    op.create_index('ix_nemra_user_templates_created_at', 'nemra_user_templates', ['created_at'], schema='report')
    
    _ = op.create_table(
        'nemra_user_pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nemra_page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('nemra_user_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['nemra_page_id'], ['report.nemra_pages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['nemra_user_template_id'], ['report.nemra_user_templates.id'], ondelete='SET NULL'),
        schema='report'
    )
    
    op.create_index('ix_nemra_user_pages_nemra_page_id', 'nemra_user_pages', ['nemra_page_id'], schema='report')
    op.create_index('ix_nemra_user_pages_nemra_user_template_id', 'nemra_user_pages', ['nemra_user_template_id'], schema='report')
    op.create_index('ix_nemra_user_pages_user_id', 'nemra_user_pages', ['user_id'], schema='report')
    op.create_index('ix_nemra_user_pages_created_at', 'nemra_user_pages', ['created_at'], schema='report')
    
    _ = op.create_table(
        'nemra_user_modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nemra_module_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('nemra_user_page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('datatypes', sa.Text(), nullable=True),
        sa.Column('is_allowed', sa.Boolean(), nullable=True),
        sa.Column('column_count', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['nemra_module_id'], ['report.nemra_modules.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['nemra_user_page_id'], ['report.nemra_user_pages.id'], ondelete='SET NULL'),
        schema='report'
    )
    
    op.create_index('ix_nemra_user_modules_nemra_module_id', 'nemra_user_modules', ['nemra_module_id'], schema='report')
    op.create_index('ix_nemra_user_modules_nemra_user_page_id', 'nemra_user_modules', ['nemra_user_page_id'], schema='report')
    op.create_index('ix_nemra_user_modules_user_id', 'nemra_user_modules', ['user_id'], schema='report')
    op.create_index('ix_nemra_user_modules_created_at', 'nemra_user_modules', ['created_at'], schema='report')


def downgrade() -> None:
    op.drop_index('ix_nemra_user_modules_created_at', table_name='nemra_user_modules', schema='report')
    op.drop_index('ix_nemra_user_modules_user_id', table_name='nemra_user_modules', schema='report')
    op.drop_index('ix_nemra_user_modules_nemra_user_page_id', table_name='nemra_user_modules', schema='report')
    op.drop_index('ix_nemra_user_modules_nemra_module_id', table_name='nemra_user_modules', schema='report')
    op.drop_table('nemra_user_modules', schema='report')
    
    op.drop_index('ix_nemra_user_pages_created_at', table_name='nemra_user_pages', schema='report')
    op.drop_index('ix_nemra_user_pages_user_id', table_name='nemra_user_pages', schema='report')
    op.drop_index('ix_nemra_user_pages_nemra_user_template_id', table_name='nemra_user_pages', schema='report')
    op.drop_index('ix_nemra_user_pages_nemra_page_id', table_name='nemra_user_pages', schema='report')
    op.drop_table('nemra_user_pages', schema='report')
    
    op.drop_index('ix_nemra_user_templates_created_at', table_name='nemra_user_templates', schema='report')
    op.drop_index('ix_nemra_user_templates_user_id', table_name='nemra_user_templates', schema='report')
    op.drop_index('ix_nemra_user_templates_nemra_user_folder_id', table_name='nemra_user_templates', schema='report')
    op.drop_index('ix_nemra_user_templates_nemra_template_id', table_name='nemra_user_templates', schema='report')
    op.drop_table('nemra_user_templates', schema='report')
    
    op.drop_index('ix_nemra_user_folders_created_at', table_name='nemra_user_folders', schema='report')
    op.drop_index('ix_nemra_user_folders_user_id', table_name='nemra_user_folders', schema='report')
    op.drop_index('ix_nemra_user_folders_nemra_folder_id', table_name='nemra_user_folders', schema='report')
    op.drop_table('nemra_user_folders', schema='report')

