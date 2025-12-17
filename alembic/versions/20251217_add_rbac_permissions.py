"""add_rbac_permissions

Revision ID: add_rbac_permissions
Revises: add_core_tables
Create Date: 2025-12-17 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "add_rbac_permissions"
down_revision: str | None = "add_core_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create schema
    op.execute('CREATE SCHEMA IF NOT EXISTS pyuser')

    _ = op.create_table(
        "rbac_permissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("role", sa.Integer(), nullable=True),
        sa.Column("resource", sa.Integer(), nullable=True),
        sa.Column("privilege", sa.Integer(), nullable=True),
        sa.Column("option", sa.Integer(), nullable=True),
        schema="pyuser",
    )

    # Enum mappings:
    # Roles: OWNER=1, ADMINISTRATOR=2, INSIDE_REP=3, OUTSIDE_REP=4
    # Resources: ADMIN=1, FACTORY=2, CUSTOMER=3, PRODUCT=4, QUOTE=5, ORDER=6, INVOICE=7, CHECK=8, CREDIT=9, EXPENSE=10, TASK=13
    # Privileges: VIEW=1, WRITE=2, DELETE=3
    # Options: OWN=1, ALL=2

    # Insert default RBAC permissions
    op.execute(
        """
        INSERT INTO pyuser.rbac_permissions (role, resource, privilege, option) VALUES
        -- OWNER permissions (full access to everything)
        (1, 1, 1, 2), (1, 1, 2, 2), (1, 1, 3, 2),  -- Admin
        (1, 2, 1, 2), (1, 2, 2, 2), (1, 2, 3, 2),  -- Factory
        (1, 3, 1, 2), (1, 3, 2, 2), (1, 3, 3, 2),  -- Customer
        (1, 4, 1, 2), (1, 4, 2, 2), (1, 4, 3, 2),  -- Product
        (1, 5, 1, 2), (1, 5, 2, 2), (1, 5, 3, 2),  -- Quote
        (1, 6, 1, 2), (1, 6, 2, 2), (1, 6, 3, 2),  -- Order
        (1, 7, 1, 2), (1, 7, 2, 2), (1, 7, 3, 2),  -- Invoice
        (1, 9, 1, 2), (1, 9, 2, 2), (1, 9, 3, 2),  -- Credit
        (1, 8, 1, 2), (1, 8, 2, 2), (1, 8, 3, 2),  -- Check
        (1, 10, 1, 2), (1, 10, 2, 2), (1, 10, 3, 2),  -- Expense
        (1, 13, 1, 2), (1, 13, 2, 2), (1, 13, 3, 2),  -- Task

        -- ADMINISTRATOR permissions (full access to everything)
        (2, 1, 1, 2), (2, 1, 2, 2), (2, 1, 3, 2),  -- Admin
        (2, 2, 1, 2), (2, 2, 2, 2), (2, 2, 3, 2),  -- Factory
        (2, 3, 1, 2), (2, 3, 2, 2), (2, 3, 3, 2),  -- Customer
        (2, 4, 1, 2), (2, 4, 2, 2), (2, 4, 3, 2),  -- Product
        (2, 5, 1, 2), (2, 5, 2, 2), (2, 5, 3, 2),  -- Quote
        (2, 6, 1, 2), (2, 6, 2, 2), (2, 6, 3, 2),  -- Order
        (2, 7, 1, 2), (2, 7, 2, 2), (2, 7, 3, 2),  -- Invoice
        (2, 9, 1, 2), (2, 9, 2, 2), (2, 9, 3, 2),  -- Credit
        (2, 8, 1, 2), (2, 8, 2, 2), (2, 8, 3, 2),  -- Check
        (2, 10, 1, 2), (2, 10, 2, 2), (2, 10, 3, 2),  -- Expense
        (2, 13, 1, 2), (2, 13, 2, 2), (2, 13, 3, 2),  -- Task

        -- INSIDE_REP permissions
        (3, 2, 1, 2), (3, 2, 2, 1), (3, 2, 3, 1),  -- Factory: view all, write/delete own
        (3, 3, 1, 2), (3, 3, 2, 1), (3, 3, 3, 1),  -- Customer: view all, write/delete own
        (3, 4, 1, 2), (3, 4, 2, 1), (3, 4, 3, 1),  -- Product: view all, write/delete own
        (3, 5, 1, 2), (3, 5, 2, 2), (3, 5, 3, 2),  -- Quote: full access
        (3, 6, 1, 2), (3, 6, 2, 2), (3, 6, 3, 2),  -- Order: full access
        (3, 7, 1, 2), (3, 7, 2, 2), (3, 7, 3, 2),  -- Invoice: full access
        (3, 9, 1, 2), (3, 9, 2, 2), (3, 9, 3, 2),  -- Credit: full access
        (3, 8, 1, 2), (3, 8, 2, 2), (3, 8, 3, 2),  -- Check: full access
        (3, 10, 1, 2), (3, 10, 2, 2), (3, 10, 3, 2),  -- Expense: full access
        (3, 13, 1, 2), (3, 13, 2, 2), (3, 13, 3, 2),  -- Task: full access

        -- OUTSIDE_REP permissions (read-only factories/customers/products, own records for transactions)
        (4, 2, 1, 2),  -- Factory: view all
        (4, 3, 1, 2),  -- Customer: view all
        (4, 4, 1, 2),  -- Product: view all
        (4, 5, 1, 1), (4, 5, 2, 1), (4, 5, 3, 1),  -- Quote: own only
        (4, 6, 1, 1), (4, 6, 2, 1), (4, 6, 3, 1),  -- Order: own only
        (4, 7, 1, 1), (4, 7, 2, 1), (4, 7, 3, 1),  -- Invoice: own only
        (4, 9, 1, 1), (4, 9, 2, 1), (4, 9, 3, 1),  -- Credit: own only
        (4, 8, 1, 1), (4, 8, 2, 1), (4, 8, 3, 1),  -- Check: own only
        (4, 10, 1, 1), (4, 10, 2, 1), (4, 10, 3, 1),  -- Expense: own only
        (4, 13, 1, 1), (4, 13, 2, 1), (4, 13, 3, 1);  -- Task: own only
        """
    )


def downgrade() -> None:
    op.drop_table("rbac_permissions", schema="pyuser")