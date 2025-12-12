"""rename_manufacturer_id_to_factory_id

Revision ID: 2b3c4d5e6f7g
Revises: 1a2b3c4d5e6f
Create Date: 2025-12-12 12:00:00.000000

"""
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5e6f7g8h9i0j'
down_revision: str | None = '4d5e6f7g8h9i'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Rename manufacturer_id column to factory_id."""
    # Drop the old index
    op.drop_index('idx_spec_sheets_manufacturer_id', table_name='spec_sheets', schema='pycrm')

    # Rename the column
    op.alter_column(
        'spec_sheets',
        'manufacturer_id',
        new_column_name='factory_id',
        schema='pycrm'
    )

    # Create the new index
    op.create_index(
        'idx_spec_sheets_factory_id',
        'spec_sheets',
        ['factory_id'],
        schema='pycrm'
    )


def downgrade() -> None:
    """Rename factory_id column back to manufacturer_id."""
    # Drop the new index
    op.drop_index('idx_spec_sheets_factory_id', table_name='spec_sheets', schema='pycrm')

    # Rename the column back
    op.alter_column(
        'spec_sheets',
        'factory_id',
        new_column_name='manufacturer_id',
        schema='pycrm'
    )

    # Create the old index
    op.create_index(
        'idx_spec_sheets_manufacturer_id',
        'spec_sheets',
        ['manufacturer_id'],
        schema='pycrm'
    )
