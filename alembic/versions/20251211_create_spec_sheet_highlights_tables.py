"""create_spec_sheet_highlights_tables

Revision ID: 4d5e6f7g8h9i
Revises: 3c4d5e6f7g8h
Create Date: 2025-12-11 18:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4d5e6f7g8h9i'
down_revision: str | None = '3c4d5e6f7g8h'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create spec_sheet_highlight_versions and spec_sheet_highlight_regions tables."""

    # Create spec_sheet_highlight_versions table
    op.create_table(
        'spec_sheet_highlight_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Reference to spec sheet
        sa.Column('spec_sheet_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Version metadata
        sa.Column('name', sa.String(255), nullable=False, server_default='Default Highlights'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key constraints
        sa.ForeignKeyConstraint(['spec_sheet_id'], ['pycrm.spec_sheets.id'], name='fk_highlight_versions_spec_sheet', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.users.id'], name='fk_highlight_versions_created_by', ondelete='RESTRICT'),

        schema='pycrm'
    )

    # Create indexes for versions table
    op.create_index(
        'idx_highlight_versions_spec_sheet_id',
        'spec_sheet_highlight_versions',
        ['spec_sheet_id'],
        schema='pycrm'
    )
    op.create_index(
        'idx_highlight_versions_is_active',
        'spec_sheet_highlight_versions',
        ['is_active'],
        schema='pycrm'
    )

    # Create spec_sheet_highlight_regions table
    op.create_table(
        'spec_sheet_highlight_regions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Reference to version
        sa.Column('version_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Page information
        sa.Column('page_number', sa.Integer(), nullable=False),

        # Position and size (percentages 0-100)
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('width', sa.Float(), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),

        # Shape properties
        sa.Column('shape_type', sa.String(50), nullable=False),
        sa.Column('color', sa.String(20), nullable=False),

        # Optional annotation
        sa.Column('annotation', sa.Text(), nullable=True),

        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key constraint
        sa.ForeignKeyConstraint(['version_id'], ['pycrm.spec_sheet_highlight_versions.id'], name='fk_highlight_regions_version', ondelete='CASCADE'),

        schema='pycrm'
    )

    # Create indexes for regions table
    op.create_index(
        'idx_highlight_regions_version_id',
        'spec_sheet_highlight_regions',
        ['version_id'],
        schema='pycrm'
    )
    op.create_index(
        'idx_highlight_regions_page_number',
        'spec_sheet_highlight_regions',
        ['page_number'],
        schema='pycrm'
    )

    # Add check constraint for shape_type
    op.create_check_constraint(
        'ck_highlight_regions_shape_type',
        'spec_sheet_highlight_regions',
        "shape_type IN ('rectangle', 'oval', 'highlight')",
        schema='pycrm'
    )


def downgrade() -> None:
    """Drop spec_sheet_highlight tables."""
    op.drop_index('idx_highlight_regions_page_number', table_name='spec_sheet_highlight_regions', schema='pycrm')
    op.drop_index('idx_highlight_regions_version_id', table_name='spec_sheet_highlight_regions', schema='pycrm')
    op.drop_table('spec_sheet_highlight_regions', schema='pycrm')

    op.drop_index('idx_highlight_versions_is_active', table_name='spec_sheet_highlight_versions', schema='pycrm')
    op.drop_index('idx_highlight_versions_spec_sheet_id', table_name='spec_sheet_highlight_versions', schema='pycrm')
    op.drop_table('spec_sheet_highlight_versions', schema='pycrm')
