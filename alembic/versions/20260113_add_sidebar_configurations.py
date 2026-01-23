"""add sidebar configurations tables

Revision ID: add_sidebar_configurations
Revises: c44a69ade93f
Create Date: 2026-01-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_sidebar_configurations"
down_revision: str | None = "c44a69ade93f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create sidebar_configurations table
    _ = op.create_table(
        "sidebar_configurations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("owner_type", sa.String(10), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.UniqueConstraint(
            "owner_type", "owner_id", "name", name="uq_sidebar_config_owner_name"
        ),
        schema="pycrm",
    )
    op.create_index(
        "ix_sidebar_configurations_owner",
        "sidebar_configurations",
        ["owner_type", "owner_id"],
        schema="pycrm",
    )

    # Create sidebar_configuration_groups table
    _ = op.create_table(
        "sidebar_configuration_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "configuration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycrm.sidebar_configurations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("group_id", sa.String(50), nullable=False),
        sa.Column("group_order", sa.Integer(), nullable=False),
        sa.Column("collapsed", sa.Boolean(), nullable=False, server_default="false"),
        sa.UniqueConstraint(
            "configuration_id", "group_id", name="uq_sidebar_config_group"
        ),
        schema="pycrm",
    )

    # Create sidebar_configuration_items table
    _ = op.create_table(
        "sidebar_configuration_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "configuration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycrm.sidebar_configurations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("group_id", sa.String(50), nullable=False),
        sa.Column("item_id", sa.String(50), nullable=False),
        sa.Column("item_order", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.UniqueConstraint(
            "configuration_id", "item_id", name="uq_sidebar_config_item"
        ),
        schema="pycrm",
    )

    # Create role_sidebar_assignments table
    _ = op.create_table(
        "role_sidebar_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role", sa.Integer(), nullable=False),
        sa.Column(
            "configuration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycrm.sidebar_configurations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("assigned_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["assigned_by_id"], ["pyuser.users.id"]),
        sa.UniqueConstraint("role", name="uq_role_sidebar_assignment_role"),
        schema="pycrm",
    )

    # Create user_active_sidebar table
    _ = op.create_table(
        "user_active_sidebar",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "configuration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycrm.sidebar_configurations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["pyuser.users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_active_sidebar_user"),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_table("user_active_sidebar", schema="pycrm")
    op.drop_table("role_sidebar_assignments", schema="pycrm")
    op.drop_table("sidebar_configuration_items", schema="pycrm")
    op.drop_table("sidebar_configuration_groups", schema="pycrm")
    op.drop_index(
        "ix_sidebar_configurations_owner",
        table_name="sidebar_configurations",
        schema="pycrm",
    )
    op.drop_table("sidebar_configurations", schema="pycrm")
