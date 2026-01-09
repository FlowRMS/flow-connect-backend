"""add nemra_templates table

Revision ID: 9159d757c059
Revises: 9c9a2f86dffe
Create Date: 2025-12-25 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '9159d757c059'
down_revision: str | None = '9c9a2f86dffe'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        'nemra_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema='report'
    )
    
    op.create_index('ix_nemra_templates_name', 'nemra_templates', ['name'], schema='report')
    
    op.execute(sa.text("""
        INSERT INTO report.nemra_templates (name) VALUES
        ('Standard ROTF'),
        ('Executive Summary Only'),
        ('Full Analysis'),
        ('Financial Focus')
        ON CONFLICT (name) DO NOTHING
    """))
    
    _ = op.create_table(
        'nemra_folder_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('folder_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['folder_id'], ['report.nemra_folders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['report.nemra_templates.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('folder_id', 'template_id', name='uq_nemra_folder_templates_folder_template'),
        schema='report'
    )
    
    op.create_index('ix_nemra_folder_templates_folder_id', 'nemra_folder_templates', ['folder_id'], schema='report')
    op.create_index('ix_nemra_folder_templates_template_id', 'nemra_folder_templates', ['template_id'], schema='report')
    
    op.execute(sa.text("""
        INSERT INTO report.nemra_folder_templates (folder_id, template_id)
        SELECT f.id, t.id
        FROM report.nemra_folders f
        CROSS JOIN report.nemra_templates t
        ON CONFLICT (folder_id, template_id) DO NOTHING
    """))


def downgrade() -> None:
    op.drop_index('ix_nemra_folder_templates_template_id', table_name='nemra_folder_templates', schema='report')
    op.drop_index('ix_nemra_folder_templates_folder_id', table_name='nemra_folder_templates', schema='report')
    op.drop_table('nemra_folder_templates', schema='report')
    op.drop_index('ix_nemra_templates_name', table_name='nemra_templates', schema='report')
    op.drop_table('nemra_templates', schema='report')

