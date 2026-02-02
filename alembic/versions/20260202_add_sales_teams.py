"""Add sales teams and members tables

Revision ID: add_sales_teams
Revises: 7702478b47b2
Create Date: 2026-02-02

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_sales_teams"
down_revision: str | None = "7702478b47b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "sales_teams",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "manager_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
        ),
        sa.Column(
            "territory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.territories.id"),
            nullable=True,
        ),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="pycore",
    )

    op.create_index(
        "ix_sales_teams_manager_id",
        "sales_teams",
        ["manager_id"],
        schema="pycore",
    )
    op.create_index(
        "ix_sales_teams_territory_id",
        "sales_teams",
        ["territory_id"],
        schema="pycore",
    )

    _ = op.create_table(
        "sales_team_members",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "sales_team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.sales_teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "sales_team_id",
            "user_id",
            name="uq_sales_team_member",
        ),
        schema="pycore",
    )

    op.create_index(
        "ix_sales_team_members_sales_team_id",
        "sales_team_members",
        ["sales_team_id"],
        schema="pycore",
    )
    op.create_index(
        "ix_sales_team_members_user_id",
        "sales_team_members",
        ["user_id"],
        schema="pycore",
    )

    # Add SALES_MANAGER (8) permissions
    # RbacPrivilegeTypeEnum: VIEW=1, WRITE=2, DELETE=3
    # RbacPrivilegeOptionEnum: OWN=1, ALL=2
    op.execute("""
        INSERT INTO pyuser.rbac_permissions (id, role, resource, privilege, option) VALUES
        -- CUSTOMER (3): VIEW, WRITE, DELETE - OWN
        (gen_random_uuid(), 8, 3, 1, 1),
        (gen_random_uuid(), 8, 3, 2, 1),
        (gen_random_uuid(), 8, 3, 3, 1),
        -- PRODUCT (4): VIEW - ALL
        (gen_random_uuid(), 8, 4, 1, 2),
        -- QUOTE (5): VIEW, WRITE, DELETE - OWN
        (gen_random_uuid(), 8, 5, 1, 1),
        (gen_random_uuid(), 8, 5, 2, 1),
        (gen_random_uuid(), 8, 5, 3, 1),
        -- ORDER (6): VIEW, WRITE, DELETE - OWN
        (gen_random_uuid(), 8, 6, 1, 1),
        (gen_random_uuid(), 8, 6, 2, 1),
        (gen_random_uuid(), 8, 6, 3, 1),
        -- INVOICE (7): VIEW - OWN
        (gen_random_uuid(), 8, 7, 1, 1),
        -- TASK (13): VIEW, WRITE, DELETE - OWN
        (gen_random_uuid(), 8, 13, 1, 1),
        (gen_random_uuid(), 8, 13, 2, 1),
        (gen_random_uuid(), 8, 13, 3, 1);
    """)


def downgrade() -> None:
    # Remove SALES_MANAGER (8) permissions
    op.execute("DELETE FROM pyuser.rbac_permissions WHERE role = 8;")

    op.drop_index(
        "ix_sales_team_members_user_id",
        table_name="sales_team_members",
        schema="pycore",
    )
    op.drop_index(
        "ix_sales_team_members_sales_team_id",
        table_name="sales_team_members",
        schema="pycore",
    )
    op.drop_table("sales_team_members", schema="pycore")

    op.drop_index(
        "ix_sales_teams_territory_id",
        table_name="sales_teams",
        schema="pycore",
    )
    op.drop_index(
        "ix_sales_teams_manager_id",
        table_name="sales_teams",
        schema="pycore",
    )
    op.drop_table("sales_teams", schema="pycore")
