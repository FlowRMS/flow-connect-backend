"""adding uq for invoice number_factory

Revision ID: 56351832b54b
Revises: insert_default_job_statuses
Create Date: 2026-01-12 09:23:27.888466

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "uq_invoice_adjustment_number"
down_revision: str | None = "insert_default_job_statuses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_invoice_number_factory",
        "invoices",
        ["invoice_number", "factory_id"],
        schema="pycommission",
    )

    op.create_unique_constraint(
        "uq_adjustment_number",
        "adjustments",
        ["adjustment_number"],
        schema="pycommission",
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_invoice_number_factory",
        "invoices",
        type_="unique",
        schema="pycommission",
    )
    op.drop_constraint(
        "uq_adjustment_number",
        "adjustments",
        type_="unique",
        schema="pycommission",
    )
