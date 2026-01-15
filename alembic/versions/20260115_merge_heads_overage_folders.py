"""merge_heads_overage_folders

Revision ID: 8a447991abdd
Revises: uq_check_details_entities, create_folders_001
Create Date: 2026-01-15 16:27:06.129464

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '8a447991abdd'
down_revision: str | None = ('uq_check_details_entities', 'create_folders_001')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    pass
    
def downgrade() -> None:
    pass
