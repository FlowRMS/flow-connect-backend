"""add_manufacturer_order_table

Revision ID: 3c4d5e6f7g8h
Revises: 2b3c4d5e6f7g
Create Date: 2025-12-11 15:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '3c4d5e6f7g8h'
down_revision: str | None = '2b3c4d5e6f7g'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create manufacturer_order table for storing custom sort order."""
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema='pycrm')

    if 'manufacturer_order' not in tables:
        op.create_table(
            'manufacturer_order',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('factory_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
            sa.UniqueConstraint('factory_id', name='uq_manufacturer_order_factory_id'),
            schema='pycrm'
        )

        # Create index on factory_id
        op.create_index(
            'idx_manufacturer_order_factory_id',
            'manufacturer_order',
            ['factory_id'],
            schema='pycrm'
        )

        # Create index on sort_order for efficient ordering
        op.create_index(
            'idx_manufacturer_order_sort_order',
            'manufacturer_order',
            ['sort_order'],
            schema='pycrm'
        )


def downgrade() -> None:
    """Drop manufacturer_order table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema='pycrm')

    if 'manufacturer_order' in tables:
        op.drop_index('idx_manufacturer_order_sort_order', table_name='manufacturer_order', schema='pycrm')
        op.drop_index('idx_manufacturer_order_factory_id', table_name='manufacturer_order', schema='pycrm')
        op.drop_table('manufacturer_order', schema='pycrm')
