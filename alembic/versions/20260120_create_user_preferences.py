"""Create user_preferences table

Revision ID: 20260120_001
Revises: 20260116_001
Create Date: 2026-01-20 17:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260120_001"
down_revision: str | None = "20260116_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application", sa.String(50), nullable=False),
        sa.Column("preference_key", sa.String(50), nullable=False),
        sa.Column("preference_value", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "application",
            "preference_key",
            name="uq_user_preferences_user_application_key",
        ),
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_table("user_preferences", schema="connect_pos")
