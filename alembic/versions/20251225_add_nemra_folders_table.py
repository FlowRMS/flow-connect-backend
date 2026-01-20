"""add nemra_folders table

Revision ID: 9c9a2f86dffe
Revises: 15c0cedaef19
Create Date: 2025-12-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "9c9a2f86dffe"
down_revision: str | None = "15c0cedaef19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "nemra_folders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema="report",
    )

    op.create_index("ix_nemra_folders_name", "nemra_folders", ["name"], schema="report")

    op.execute(
        sa.text("""
        INSERT INTO report.nemra_folders (name) VALUES
        ('NEMRA Line Reviews'),
        ('DISC')
        ON CONFLICT (name) DO NOTHING
    """)
    )


def downgrade() -> None:
    op.drop_index("ix_nemra_folders_name", table_name="nemra_folders", schema="report")
    op.drop_table("nemra_folders", schema="report")
