"""first revision

Revision ID: 6f462a3f0a59
Revises: 62e4315e9e63
Create Date: 2025-10-09 16:43:51.169236

"""
from collections.abc import Sequence


revision: str = '6f462a3f0a59'
down_revision: str | None = '62e4315e9e63'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    # report_templates table is already created in migration 983952e7b210 (20251229_adding_report_models.py)
    # No schema changes needed in this migration
    pass

def downgrade() -> None:
    # No schema changes to revert
    pass