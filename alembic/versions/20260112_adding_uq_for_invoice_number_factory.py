"""adding uq for invoice number_factory

Revision ID: 56351832b54b
Revises: insert_default_job_statuses
Create Date: 2026-01-12 09:23:27.888466

"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "uq_invoice_adjustment_number"
down_revision: str | None = "insert_default_job_statuses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def constraint_exists(constraint_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        text("""
            SELECT 1 FROM pg_constraint
            WHERE conname = :name
        """),
        {"name": constraint_name},
    )
    return result.fetchone() is not None


def upgrade() -> None:
    if not constraint_exists("uq_invoice_number_factory"):
        # Deduplicate invoice_number + factory_id by appending -1, -2, etc.
        op.execute("""
            WITH duplicates AS (
                SELECT
                    id,
                    invoice_number,
                    factory_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY invoice_number, factory_id
                        ORDER BY created_at, id
                    ) AS rn
                FROM pycommission.invoices
            )
            UPDATE pycommission.invoices i
            SET invoice_number = i.invoice_number || '-' || (d.rn - 1)::text
            FROM duplicates d
            WHERE i.id = d.id AND d.rn > 1
        """)

        op.create_unique_constraint(
            "uq_invoice_number_factory",
            "invoices",
            ["invoice_number", "factory_id"],
            schema="pycommission",
        )

    if not constraint_exists("uq_adjustment_number"):
        # Deduplicate adjustment_number by appending -1, -2, etc.
        op.execute("""
            WITH duplicates AS (
                SELECT
                    id,
                    adjustment_number,
                    ROW_NUMBER() OVER (
                        PARTITION BY adjustment_number
                        ORDER BY created_at, id
                    ) AS rn
                FROM pycommission.adjustments
            )
            UPDATE pycommission.adjustments a
            SET adjustment_number = a.adjustment_number || '-' || (d.rn - 1)::text
            FROM duplicates d
            WHERE a.id = d.id AND d.rn > 1
        """)

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
