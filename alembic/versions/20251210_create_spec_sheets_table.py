"""create_spec_sheets_table

Revision ID: 1a2b3c4d5e6f
Revises: c4b9f784a484
Create Date: 2025-12-10 17:30:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: str | None = 'c4b9f784a484'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create spec_sheets table."""
    op.create_table(
        'spec_sheets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Basic Information
        sa.Column('factory_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),

        # Upload Information
        sa.Column('upload_source', sa.String(50), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('file_url', sa.Text(), nullable=False),

        # File Metadata
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False, server_default='1'),

        # Categorization
        sa.Column('categories', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),

        # Status
        sa.Column('needs_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('published', sa.Boolean(), nullable=False, server_default='true'),

        # Usage tracking
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('highlight_count', sa.Integer(), nullable=False, server_default='0'),

        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key constraint
        sa.ForeignKeyConstraint(['created_by_id'], ['user.users.id'], name='fk_spec_sheets_created_by', ondelete='RESTRICT'),

        schema='pycrm'
    )

    # Create indexes
    op.create_index(
        'idx_spec_sheets_factory_id',
        'spec_sheets',
        ['factory_id'],
        schema='pycrm'
    )
    op.create_index(
        'idx_spec_sheets_categories',
        'spec_sheets',
        ['categories'],
        schema='pycrm',
        postgresql_using='gin'
    )
    op.create_index(
        'idx_spec_sheets_published',
        'spec_sheets',
        ['published'],
        schema='pycrm'
    )
    op.create_index(
        'idx_spec_sheets_created_at',
        'spec_sheets',
        [sa.text('created_at DESC')],
        schema='pycrm'
    )
    op.create_index(
        'idx_spec_sheets_display_name',
        'spec_sheets',
        ['display_name'],
        schema='pycrm'
    )

    # Add check constraint for upload_source
    op.create_check_constraint(
        'ck_spec_sheets_upload_source',
        'spec_sheets',
        "upload_source IN ('url', 'file')",
        schema='pycrm'
    )


def downgrade() -> None:
    """Drop spec_sheets table."""
    op.drop_index('idx_spec_sheets_display_name', table_name='spec_sheets', schema='pycrm')
    op.drop_index('idx_spec_sheets_created_at', table_name='spec_sheets', schema='pycrm')
    op.drop_index('idx_spec_sheets_published', table_name='spec_sheets', schema='pycrm')
    op.drop_index('idx_spec_sheets_categories', table_name='spec_sheets', schema='pycrm')
    op.drop_index('idx_spec_sheets_factory_id', table_name='spec_sheets', schema='pycrm')
    op.drop_table('spec_sheets', schema='pycrm')
