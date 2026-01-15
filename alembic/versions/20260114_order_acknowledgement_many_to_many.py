"""order_acknowledgement_many_to_many

Revision ID: order_ack_m2m_001
Revises: uq_check_details_entities
Create Date: 2026-01-14

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "order_ack_m2m_001"
down_revision: str | None = "uq_check_details_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "order_acknowledgement_details",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_acknowledgement_id", sa.UUID(), nullable=False),
        sa.Column("order_detail_id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_acknowledgement_id"],
            ["pycommission.order_acknowledgements.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["order_detail_id"],
            ["pycommission.order_details.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "order_acknowledgement_id",
            "order_detail_id",
            name="uq_order_acknowledgement_detail",
        ),
        schema="pycommission",
    )
    op.create_index(
        "ix_order_ack_details_acknowledgement_id",
        "order_acknowledgement_details",
        ["order_acknowledgement_id"],
        schema="pycommission",
    )
    op.create_index(
        "ix_order_ack_details_detail_id",
        "order_acknowledgement_details",
        ["order_detail_id"],
        schema="pycommission",
    )

    op.execute(
        """
        INSERT INTO pycommission.order_acknowledgement_details
            (id, order_acknowledgement_id, order_detail_id, created_by_id, created_at)
        SELECT
            gen_random_uuid(),
            id,
            order_detail_id,
            created_by_id,
            created_at
        FROM pycommission.order_acknowledgements
        WHERE order_detail_id IS NOT NULL
        """
    )

    op.drop_index(
        "ix_order_acknowledgements_order_detail_id",
        table_name="order_acknowledgements",
        schema="pycommission",
    )
    op.drop_constraint(
        "order_acknowledgements_order_detail_id_fkey",
        "order_acknowledgements",
        schema="pycommission",
        type_="foreignkey",
    )
    op.drop_column("order_acknowledgements", "order_detail_id", schema="pycommission")


def downgrade() -> None:
    op.add_column(
        "order_acknowledgements",
        sa.Column("order_detail_id", sa.UUID(), nullable=True),
        schema="pycommission",
    )

    op.execute(
        """
        UPDATE pycommission.order_acknowledgements oa
        SET order_detail_id = (
            SELECT oad.order_detail_id
            FROM pycommission.order_acknowledgement_details oad
            WHERE oad.order_acknowledgement_id = oa.id
            LIMIT 1
        )
        """
    )

    op.alter_column(
        "order_acknowledgements",
        "order_detail_id",
        nullable=False,
        schema="pycommission",
    )
    op.create_foreign_key(
        "order_acknowledgements_order_detail_id_fkey",
        "order_acknowledgements",
        "order_details",
        ["order_detail_id"],
        ["id"],
        source_schema="pycommission",
        referent_schema="pycommission",
    )
    op.create_index(
        "ix_order_acknowledgements_order_detail_id",
        "order_acknowledgements",
        ["order_detail_id"],
        schema="pycommission",
    )

    op.drop_index(
        "ix_order_ack_details_detail_id",
        table_name="order_acknowledgement_details",
        schema="pycommission",
    )
    op.drop_index(
        "ix_order_ack_details_acknowledgement_id",
        table_name="order_acknowledgement_details",
        schema="pycommission",
    )
    op.drop_table("order_acknowledgement_details", schema="pycommission")
