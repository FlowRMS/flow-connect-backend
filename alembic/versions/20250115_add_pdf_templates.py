"""add pdf templates

Revision ID: add_pdf_templates
Revises: add_contact_type_contacts
Create Date: 2025-01-15

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'add_pdf_templates'
down_revision: str | None = '4d5e6f7g8h9i'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create user schema if it doesn't exist (needed for foreign key references)
    op.execute('CREATE SCHEMA IF NOT EXISTS "user"')
    
    # Create stub users table in user schema if it doesn't exist
    # This is a minimal table to satisfy foreign key constraints
    # The actual data will be migrated separately
    op.execute("""
        CREATE TABLE IF NOT EXISTS "user".users (
            id UUID PRIMARY KEY
        )
    """)
    
    # Create pdf_template_types table (must be created first as it's referenced by pdf_templates)
    op.create_table(
        'pdf_template_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.users.id'], name='fk_pdf_template_types_created_by_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_pdf_template_types_name'),
        schema='pycrm'
    )

    # Create index on pdf_template_types
    op.create_index(
        'ix_pycrm_pdf_template_types_name',
        'pdf_template_types',
        ['name'],
        schema='pycrm'
    )

    # Create pdf_templates table
    op.create_table(
        'pdf_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_type_code', sa.String(length=50), nullable=False),
        sa.Column('template_type_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('global_styles', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.users.id'], name='fk_pdf_templates_created_by_id'),
        sa.ForeignKeyConstraint(['template_type_id'], ['pycrm.pdf_template_types.id'], name='fk_pdf_templates_template_type_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='pycrm'
    )

    # Create indexes on pdf_templates
    op.create_index(
        'ix_pycrm_pdf_templates_template_type_code',
        'pdf_templates',
        ['template_type_code'],
        schema='pycrm'
    )
    op.create_index(
        'ix_pycrm_pdf_templates_template_type_id',
        'pdf_templates',
        ['template_type_id'],
        schema='pycrm'
    )
    op.create_index(
        'ix_pycrm_pdf_templates_name',
        'pdf_templates',
        ['name'],
        schema='pycrm'
    )
    op.create_index(
        'ix_pycrm_pdf_templates_is_default',
        'pdf_templates',
        ['template_type_code', 'is_default'],
        schema='pycrm'
    )

    # Create pdf_template_modules table
    op.create_table(
        'pdf_template_modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('module_type', sa.String(length=50), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['template_id'], ['pycrm.pdf_templates.id'], name='fk_pdf_template_modules_template_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='pycrm'
    )

    # Create indexes on pdf_template_modules
    op.create_index(
        'ix_pycrm_pdf_template_modules_template_id',
        'pdf_template_modules',
        ['template_id'],
        schema='pycrm'
    )
    op.create_index(
        'ix_pycrm_pdf_template_modules_position',
        'pdf_template_modules',
        ['template_id', 'position'],
        schema='pycrm'
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_pycrm_pdf_template_modules_position', table_name='pdf_template_modules', schema='pycrm')
    op.drop_index('ix_pycrm_pdf_template_modules_template_id', table_name='pdf_template_modules', schema='pycrm')
    op.drop_index('ix_pycrm_pdf_templates_is_default', table_name='pdf_templates', schema='pycrm')
    op.drop_index('ix_pycrm_pdf_templates_name', table_name='pdf_templates', schema='pycrm')
    op.drop_index('ix_pycrm_pdf_templates_template_type_id', table_name='pdf_templates', schema='pycrm')
    op.drop_index('ix_pycrm_pdf_templates_template_type_code', table_name='pdf_templates', schema='pycrm')
    op.drop_index('ix_pycrm_pdf_template_types_name', table_name='pdf_template_types', schema='pycrm')

    # Drop tables in reverse order (modules first, then templates, then types)
    op.drop_table('pdf_template_modules', schema='pycrm')
    op.drop_table('pdf_templates', schema='pycrm')
    op.drop_table('pdf_template_types', schema='pycrm')

