from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "d627dc1dbf6e"
down_revision: str | None = "005587d19685"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "order_acknowledgements",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("order_detail_id", sa.UUID(), nullable=False),
        sa.Column(
            "order_acknowledgement_number", sa.String(length=255), nullable=False
        ),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column(
            "quantity",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
        ),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["pycommission.orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_detail_id"],
            ["pycommission.order_details.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )
    op.create_index(
        "ix_order_acknowledgements_order_id",
        "order_acknowledgements",
        ["order_id"],
        schema="pycommission",
    )
    op.create_index(
        "ix_order_acknowledgements_order_detail_id",
        "order_acknowledgements",
        ["order_detail_id"],
        schema="pycommission",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_order_acknowledgements_order_detail_id",
        table_name="order_acknowledgements",
        schema="pycommission",
    )
    op.drop_index(
        "ix_order_acknowledgements_order_id",
        table_name="order_acknowledgements",
        schema="pycommission",
    )
    op.drop_table("order_acknowledgements", schema="pycommission")
