"""add submittal config fields

Revision ID: submittal_config_001
Revises: cascade_del_regions
Create Date: 2026-01-19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "submittal_config_001"
down_revision: str | None = "cascade_del_regions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add config columns to submittals table
    op.add_column(
        "submittals",
        sa.Column(
            "config_include_lamps",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_include_accessories",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_include_cq",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_include_from_orders",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_roll_up_kits",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_roll_up_accessories",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_include_zero_quantity_items",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_drop_descriptions",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycrm",
    )
    op.add_column(
        "submittals",
        sa.Column(
            "config_drop_line_notes",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("submittals", "config_drop_line_notes", schema="pycrm")
    op.drop_column("submittals", "config_drop_descriptions", schema="pycrm")
    op.drop_column("submittals", "config_include_zero_quantity_items", schema="pycrm")
    op.drop_column("submittals", "config_roll_up_accessories", schema="pycrm")
    op.drop_column("submittals", "config_roll_up_kits", schema="pycrm")
    op.drop_column("submittals", "config_include_from_orders", schema="pycrm")
    op.drop_column("submittals", "config_include_cq", schema="pycrm")
    op.drop_column("submittals", "config_include_accessories", schema="pycrm")
    op.drop_column("submittals", "config_include_lamps", schema="pycrm")
