"""Insert default UOMs with division factors

Revision ID: insert_default_uoms_001
Revises: warehouse_settings_001
Create Date: 2025-01-01

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "insert_default_uoms_001"
down_revision: str | None = "warehouse_settings_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_UOMS = [
    ("ea", 1),
    ("m", 1000),
    ("mft", 1000),
    ("d", 500),
    ("100/ft", 100),
    ("ft", 100),
    ("c", 100),
    ("l", 50),
    ("x", 10),
    ("v", 5),
]


def upgrade() -> None:
    # Drop column if it exists (may already be removed in some environments)
    op.execute("ALTER TABLE pycore.product_uoms DROP COLUMN IF EXISTS created_by_id")
    for title, division_factor in DEFAULT_UOMS:
        op.execute(f"""
            INSERT INTO pycore.product_uoms (id, title, division_factor, creation_type, created_at)
            VALUES (
                gen_random_uuid(),
                '{title}',
                {division_factor},
                1,
                NOW()
            )
            ON CONFLICT DO NOTHING
        """)


def downgrade() -> None:
    titles = ", ".join(f"'{title}'" for title, _ in DEFAULT_UOMS)
    op.execute(f"""
        DELETE FROM pycore.product_uoms
        WHERE title IN ({titles})
        AND creation_type = 1
    """)

    op.add_column(
        "product_uoms",
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        schema="pycore",
    )
