"""add unique constraints to check_details

Revision ID: uq_check_details_entities
Revises: 7c44527b01d1
Create Date: 2026-01-14

"""

from collections.abc import Sequence

from alembic import op

revision: str = "uq_check_details_entities"
down_revision: str | None = "7c44527b01d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_check_details_invoice_id",
        "check_details",
        ["invoice_id"],
        schema="pycommission",
    )

    op.create_unique_constraint(
        "uq_check_details_credit_id",
        "check_details",
        ["credit_id"],
        schema="pycommission",
    )

    op.create_unique_constraint(
        "uq_check_details_adjustment_id",
        "check_details",
        ["adjustment_id"],
        schema="pycommission",
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_check_details_invoice_id",
        "check_details",
        type_="unique",
        schema="pycommission",
    )
    op.drop_constraint(
        "uq_check_details_credit_id",
        "check_details",
        type_="unique",
        schema="pycommission",
    )
    op.drop_constraint(
        "uq_check_details_adjustment_id",
        "check_details",
        type_="unique",
        schema="pycommission",
    )
