"""add gmail user tokens

Revision ID: c3d4e5f60718
Revises: b2c3d4e5f607
Create Date: 2025-12-08 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f60718"
down_revision: str | None = "b2c3d4e5f607"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "gmail_user_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("google_user_id", sa.String(length=255), nullable=False),
        sa.Column("google_email", sa.String(length=255), nullable=False),
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
            name="fk_gmail_user_tokens_user_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_gmail_user_tokens_user_id"),
        schema="pycrm",
    )

    op.create_index(
        "ix_gmail_user_tokens_user_id",
        "gmail_user_tokens",
        ["user_id"],
        schema="pycrm",
    )

    op.create_index(
        "ix_gmail_user_tokens_google_user_id",
        "gmail_user_tokens",
        ["google_user_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_gmail_user_tokens_google_user_id",
        table_name="gmail_user_tokens",
        schema="pycrm",
    )
    op.drop_index(
        "ix_gmail_user_tokens_user_id",
        table_name="gmail_user_tokens",
        schema="pycrm",
    )
    op.drop_table("gmail_user_tokens", schema="pycrm")
