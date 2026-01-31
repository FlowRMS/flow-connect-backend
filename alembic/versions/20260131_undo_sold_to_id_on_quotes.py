"""undo sold to id on quotes

Revision ID: f436cbb68e04
Revises: commons_v3_schema_changes
Create Date: 2026-01-31 11:56:14.574558

"""
from collections.abc import Sequence

from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'undo_null_sold_to'
down_revision: str | None = 'commons_v3_schema_changes'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.alter_column(
        'quotes',
        'sold_to_customer_id',
        existing_type=postgresql.UUID(),
        nullable=False,
    )

    
def downgrade() -> None:
    op.alter_column(
        'quotes',
        'sold_to_customer_id',
        existing_type=postgresql.UUID(),
        nullable=True,
    )