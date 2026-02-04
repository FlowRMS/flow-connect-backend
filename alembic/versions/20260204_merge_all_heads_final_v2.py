"""merge_all_heads_final_v2

Revision ID: a098b96eeb0f
Revises: add_factory_customer_references, e1824a0cf94c
Create Date: 2026-02-04 14:24:51.564551

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = 'a098b96eeb0f'
down_revision: str | None = ('add_factory_customer_references', 'e1824a0cf94c')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    pass
    
def downgrade() -> None:
    pass
