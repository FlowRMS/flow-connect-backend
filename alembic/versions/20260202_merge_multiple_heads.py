"""merge_multiple_heads

Revision ID: 5630cc7582d0
Revises: undo_null_sold_to, a9ce29443448
Create Date: 2026-02-02 13:20:59.075271

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '5630cc7582d0'
down_revision: str | None = ('undo_null_sold_to', 'a9ce29443448')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    pass
    
def downgrade() -> None:
    pass
