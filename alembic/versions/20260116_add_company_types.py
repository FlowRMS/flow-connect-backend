"""Add company_types table and migrate from enum

Revision ID: add_company_types
Revises: add_task_categories
Create Date: 2026-01-16

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_company_types"
down_revision: str | None = "add_task_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Mapping from old enum int values to names (matching CompanyType IntEnum)
LEGACY_COMPANY_TYPES = {
    1: "Customer",
    2: "Manufacturer",
    3: "Engineering Firm",
    4: "Consulting Engineer",
    5: "Electrical Engineer",
    6: "MEP Engineer",
    7: "Architect",
    8: "Lighting Designer",
    9: "Specifier",
    10: "Electrical Contractor",
    11: "General Contractor",
    12: "Design Build Firm",
    13: "EPC",
    14: "Systems Integrator",
    15: "Controls Contractor",
    16: "Low Voltage Contractor",
    17: "Building Owner",
    18: "Developer",
    19: "Property Management Company",
    20: "Facility Management Company",
    21: "Utility Company",
    22: "Municipality / Public Authority",
    23: "AHJ",
    24: "Commissioning Agent",
    25: "Testing / Inspection Agency",
    26: "Energy Program Administrator",
    27: "Trade Association",
}


def upgrade() -> None:
    # Create company_types table
    op.create_table(
        "company_types",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="pycrm",
    )

    # Create index on name
    op.create_index(
        "ix_company_types_name",
        "company_types",
        ["name"],
        schema="pycrm",
    )

    # Seed company types from legacy enum values
    values = ", ".join(
        f"(gen_random_uuid(), '{name}', {order})"
        for order, name in LEGACY_COMPANY_TYPES.items()
    )
    op.execute(f"INSERT INTO pycrm.company_types (id, name, display_order) VALUES {values};")

    # Add company_type_id column to companies
    op.add_column(
        "companies",
        sa.Column(
            "company_type_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema="pycrm",
    )

    # Migrate existing company_source_type int values to company_type_id UUIDs
    op.execute("""
        UPDATE pycrm.companies c
        SET company_type_id = ct.id
        FROM pycrm.company_types ct
        WHERE ct.display_order = c.company_source_type;
    """)

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_companies_company_type_id",
        "companies",
        "company_types",
        ["company_type_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycrm",
        ondelete="SET NULL",
    )

    # Create index on company_type_id
    op.create_index(
        "ix_companies_company_type_id",
        "companies",
        ["company_type_id"],
        schema="pycrm",
    )

    # Drop the old company_source_type column
    op.drop_column("companies", "company_source_type", schema="pycrm")


def downgrade() -> None:
    # Re-add company_source_type column
    op.add_column(
        "companies",
        sa.Column("company_source_type", sa.Integer(), nullable=True),
        schema="pycrm",
    )

    # Migrate company_type_id back to company_source_type
    op.execute("""
        UPDATE pycrm.companies c
        SET company_source_type = ct.display_order
        FROM pycrm.company_types ct
        WHERE ct.id = c.company_type_id;
    """)

    # Drop index on company_type_id
    op.drop_index("ix_companies_company_type_id", table_name="companies", schema="pycrm")

    # Drop foreign key constraint
    op.drop_constraint(
        "fk_companies_company_type_id", "companies", schema="pycrm", type_="foreignkey"
    )

    # Drop company_type_id column
    op.drop_column("companies", "company_type_id", schema="pycrm")

    # Drop index on company_types
    op.drop_index("ix_company_types_name", table_name="company_types", schema="pycrm")

    # Drop company_types table
    op.drop_table("company_types", schema="pycrm")
