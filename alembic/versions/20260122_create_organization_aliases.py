"""Create organization_aliases table

Revision ID: 20260122_001
Revises: 20260121_001
Create Date: 2026-01-22 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260122_001"
down_revision: str | None = "20260121_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connected_org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alias", sa.String(255), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "connected_org_id",
            name="uq_organization_aliases_org_connected",
        ),
        schema="connect_pos",
    )

    op.create_index(
        "ix_organization_aliases_organization_id",
        "organization_aliases",
        ["organization_id"],
        schema="connect_pos",
    )

    op.execute(
        """
        CREATE UNIQUE INDEX uq_organization_aliases_org_alias_lower
        ON connect_pos.organization_aliases (organization_id, LOWER(alias))
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS connect_pos.uq_organization_aliases_org_alias_lower")
    op.drop_index(
        "ix_organization_aliases_organization_id",
        table_name="organization_aliases",
        schema="connect_pos",
    )
    op.drop_table("organization_aliases", schema="connect_pos")
