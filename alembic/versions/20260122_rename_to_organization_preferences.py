"""Rename user_preferences to organization_preferences

Revision ID: 20260122_001
Revises: 20260120_001
Create Date: 2026-01-22 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260122_002"
down_revision: str | None = "20260122_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_user_preferences_user_application_key",
        "user_preferences",
        schema="connect_pos",
    )
    op.alter_column(
        "user_preferences",
        "user_id",
        new_column_name="organization_id",
        schema="connect_pos",
    )
    op.rename_table(
        "user_preferences",
        "organization_preferences",
        schema="connect_pos",
    )
    op.create_unique_constraint(
        "uq_org_preferences_org_application_key",
        "organization_preferences",
        ["organization_id", "application", "preference_key"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_org_preferences_org_application_key",
        "organization_preferences",
        schema="connect_pos",
    )
    op.rename_table(
        "organization_preferences",
        "user_preferences",
        schema="connect_pos",
    )
    op.alter_column(
        "user_preferences",
        "organization_id",
        new_column_name="user_id",
        schema="connect_pos",
    )
    op.create_unique_constraint(
        "uq_user_preferences_user_application_key",
        "user_preferences",
        ["user_id", "application", "preference_key"],
        schema="connect_pos",
    )
