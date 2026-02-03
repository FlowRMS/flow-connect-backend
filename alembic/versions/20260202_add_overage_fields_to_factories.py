# add overage fields to factories
# Revision ID: add_overage_fields
# Revises: add_factory_parent_child
# Create Date: 2026-02-02

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_overage_fields"
down_revision: str | None = "add_factory_parent_child"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Use IF NOT EXISTS to make migration idempotent
    op.execute("""
        ALTER TABLE pycore.factories
        ADD COLUMN IF NOT EXISTS overage_allowed BOOLEAN DEFAULT false NOT NULL
    """)
    op.execute("""
        ALTER TABLE pycore.factories
        ADD COLUMN IF NOT EXISTS overage_type SMALLINT DEFAULT 0 NOT NULL
    """)
    op.execute("""
        ALTER TABLE pycore.factories
        ADD COLUMN IF NOT EXISTS rep_overage_share NUMERIC(5, 2) DEFAULT 100.00 NOT NULL
    """)


def downgrade() -> None:
    op.drop_column("factories", "rep_overage_share", schema="pycore")
    op.drop_column("factories", "overage_type", schema="pycore")
    op.drop_column("factories", "overage_allowed", schema="pycore")
