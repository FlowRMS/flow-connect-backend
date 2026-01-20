"""add service_type to fulfillment_orders

Revision ID: add_service_type_to_fulfillment
Revises: allow_null_zip_code
Create Date: 2026-01-20

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "add_service_type_to_fulfillment"
down_revision: str | None = "allow_null_zip_code"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "fulfillment_orders",
        sa.Column("service_type", sa.String(100), nullable=True),
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_column("fulfillment_orders", "service_type", schema="pywarehouse")
