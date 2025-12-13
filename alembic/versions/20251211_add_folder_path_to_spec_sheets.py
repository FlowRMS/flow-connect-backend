"""add_folder_path_to_spec_sheets

Revision ID: 2b3c4d5e6f7g
Revises: 1a2b3c4d5e6f
Create Date: 2025-12-11 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '2b3c4d5e6f7g'
down_revision: str | None = '1a2b3c4d5e6f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add folder_path column to spec_sheets table."""
    # Check if column already exists
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('spec_sheets', schema='pycrm')]
    
    if 'folder_path' not in columns:
        op.add_column(
            'spec_sheets',
            sa.Column('folder_path', sa.String(500), nullable=True),
            schema='pycrm'
        )
    
    # Check if index already exists
    indexes = [idx['name'] for idx in inspector.get_indexes('spec_sheets', schema='pycrm')]
    if 'idx_spec_sheets_folder_path' not in indexes:
        op.create_index(
            'idx_spec_sheets_folder_path',
            'spec_sheets',
            ['folder_path'],
            schema='pycrm'
        )


def downgrade() -> None:
    """Remove folder_path column from spec_sheets table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    
    indexes = [idx['name'] for idx in inspector.get_indexes('spec_sheets', schema='pycrm')]
    if 'idx_spec_sheets_folder_path' in indexes:
        op.drop_index('idx_spec_sheets_folder_path', table_name='spec_sheets', schema='pycrm')
    
    columns = [col['name'] for col in inspector.get_columns('spec_sheets', schema='pycrm')]
    if 'folder_path' in columns:
        op.drop_column('spec_sheets', 'folder_path', schema='pycrm')
