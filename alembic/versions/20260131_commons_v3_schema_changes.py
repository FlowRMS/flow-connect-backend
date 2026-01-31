"""commons v3 schema changes: quote name + nullable sold_to, notifications, freight_categories, setting keys

Revision ID: commons_v3_schema_changes
Revises: tags_core_entities
Create Date: 2026-01-31 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "commons_v3_schema_changes"
down_revision: str | None = "tags_core_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- Quotes: add name column, make sold_to_customer_id nullable ---
    op.add_column(
        "quotes",
        sa.Column("name", sa.String(255), nullable=True),
        schema="pycrm",
    )
    op.alter_column(
        "quotes",
        "sold_to_customer_id",
        existing_type=UUID(as_uuid=True),
        nullable=True,
        schema="pycrm",
    )

    # --- Notifications table ---
    _ = op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("entity_type", sa.Integer, nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("notification_type", sa.Integer, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column(
            "is_read", sa.Boolean, nullable=False, server_default=sa.text("false")
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        schema="pycore",
    )

    # --- Freight categories table ---
    _ = op.create_table(
        "freight_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("freight_class", sa.Numeric(5, 1), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column(
            "is_active", sa.Boolean, nullable=False, server_default=sa.text("true")
        ),
        sa.Column("position", sa.Integer, nullable=False, server_default=sa.text("0")),
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_table("freight_categories", schema="pywarehouse")
    op.drop_table("notifications", schema="pycore")

    op.alter_column(
        "quotes",
        "sold_to_customer_id",
        existing_type=UUID(as_uuid=True),
        nullable=False,
        schema="pycrm",
    )
    op.drop_column("quotes", "name", schema="pycrm")
