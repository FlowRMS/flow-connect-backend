"""merge_user_migrations_with_existing

Revision ID: d827079a2904
Revises: add_visible_to_users, b2c3d4e5f6a7
Create Date: 2026-01-09 20:45:27.279105

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = 'd827079a2904'
down_revision: str | None = ('add_visible_to_users', 'b2c3d4e5f6a7')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    pass
    
def downgrade() -> None:
    pass
