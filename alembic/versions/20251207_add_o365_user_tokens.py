"""add o365 user tokens

Revision ID: b2c3d4e5f607
Revises: 9d142b0d8f38
Create Date: 2025-12-07 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f607"
down_revision: str | None = "a5e7c9d2b4f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "o365_user_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("microsoft_user_id", sa.String(length=255), nullable=False),
        sa.Column("microsoft_email", sa.String(length=255), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=False),
        sa.Column(
            "token_type",
            sa.String(length=50),
            nullable=False,
            server_default="Bearer",
        ),
        sa.Column("expires_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_used_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.users.id"],
            name="fk_o365_user_tokens_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_o365_user_tokens_user_id"),
        schema="pycrm",
    )

    op.create_index(
        "ix_o365_user_tokens_user_id",
        "o365_user_tokens",
        ["user_id"],
        schema="pycrm",
    )

    op.create_index(
        "ix_o365_user_tokens_microsoft_user_id",
        "o365_user_tokens",
        ["microsoft_user_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_o365_user_tokens_microsoft_user_id",
        table_name="o365_user_tokens",
        schema="pycrm",
    )
    op.drop_index(
        "ix_o365_user_tokens_user_id",
        table_name="o365_user_tokens",
        schema="pycrm",
    )
    op.drop_table("o365_user_tokens", schema="pycrm")
