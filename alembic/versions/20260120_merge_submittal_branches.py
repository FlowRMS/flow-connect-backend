"""merge_submittal_branches

Revision ID: 2adbedfe0eff
Revises: submittal_config_001, add_submittal_settings_fields
Create Date: 2026-01-20 12:17:57.300572

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '2adbedfe0eff'
down_revision: str | None = ('submittal_config_001', 'add_submittal_settings_fields')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    pass
    
def downgrade() -> None:
    pass
