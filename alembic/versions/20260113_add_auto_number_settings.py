"""add auto number settings

Revision ID: add_auto_number_settings
Revises: fulfillment_address_fk
Create Date: 2026-01-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_auto_number_settings"
down_revision: str | None = "fulfillment_address_fk"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "auto_number_settings",
        sa.Column("entity_type", sa.SmallInteger(), nullable=False),
        sa.Column(
            "prefix",
            sa.String(length=255),
            nullable=False,
            server_default="Flow-",
        ),
        sa.Column(
            "starts_at",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "increment_by",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "counter",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "allow_auto_generation",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "entity_type",
            name="uq_auto_number_settings_entity_type",
        ),
        schema="pycore",
    )
    op.create_index(
        "ix_pycore_auto_number_settings_entity_type",
        "auto_number_settings",
        ["entity_type"],
        unique=False,
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_pycore_auto_number_settings_entity_type",
        table_name="auto_number_settings",
        schema="pycore",
    )
    op.drop_table("auto_number_settings", schema="pycore")
