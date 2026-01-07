"""Add freight_class to shipping_carriers.

Revision ID: 20260107_freight_class
Revises: 20260107_documents
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260107_freight_class'
down_revision = '20260107_documents'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add freight_class column to shipping_carriers
    op.add_column(
        'shipping_carriers',
        sa.Column('freight_class', sa.String(10), nullable=True),
        schema='pywarehouse'
    )


def downgrade() -> None:
    # Remove freight_class column
    op.drop_column('shipping_carriers', 'freight_class', schema='pywarehouse')
