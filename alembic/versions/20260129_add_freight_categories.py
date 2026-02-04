"""Add freight_categories table for warehouse settings

Revision ID: add_freight_categories
Revises: quotes_orders_sold_to_nullable
Create Date: 2026-01-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_freight_categories"
down_revision: str | None = "quotes_orders_sold_to_nullable"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "freight_categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("freight_class", sa.Numeric(5, 1), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="pywarehouse",
    )

    op.create_index(
        "ix_freight_categories_freight_class",
        "freight_categories",
        ["freight_class"],
        schema="pywarehouse",
    )

    op.create_index(
        "ix_freight_categories_position",
        "freight_categories",
        ["position"],
        schema="pywarehouse",
    )

    # Seed standard NMFC freight classes
    op.execute("""
        INSERT INTO pywarehouse.freight_categories (id, freight_class, description, position) VALUES
        (gen_random_uuid(), 50, 'Clean freight, fits on standard pallet', 1),
        (gen_random_uuid(), 55, 'Bricks, cement, hardwood flooring', 2),
        (gen_random_uuid(), 60, 'Car accessories, car parts', 3),
        (gen_random_uuid(), 65, 'Car parts, bottled beverages', 4),
        (gen_random_uuid(), 70, 'Newspapers, wooden pencils', 5),
        (gen_random_uuid(), 77.5, 'Tires, bathroom fixtures', 6),
        (gen_random_uuid(), 85, 'Crated machinery, cast iron stoves', 7),
        (gen_random_uuid(), 92.5, 'Computers, monitors, refrigerators', 8),
        (gen_random_uuid(), 100, 'Boat covers, car covers, wine cases', 9),
        (gen_random_uuid(), 110, 'Cabinets, framed paintings', 10),
        (gen_random_uuid(), 125, 'Small household appliances', 11),
        (gen_random_uuid(), 150, 'Auto sheet metal, bookcases', 12),
        (gen_random_uuid(), 175, 'Clothing, couches', 13),
        (gen_random_uuid(), 200, 'Sheet rock, plywood', 14),
        (gen_random_uuid(), 250, 'Bamboo furniture, mattresses', 15),
        (gen_random_uuid(), 300, 'Model boats, wood cabinets', 16),
        (gen_random_uuid(), 400, 'Deer antlers', 17),
        (gen_random_uuid(), 500, 'Low density/high value items', 18);
    """)


def downgrade() -> None:
    op.drop_index(
        "ix_freight_categories_position",
        table_name="freight_categories",
        schema="pywarehouse",
    )
    op.drop_index(
        "ix_freight_categories_freight_class",
        table_name="freight_categories",
        schema="pywarehouse",
    )
    op.drop_table("freight_categories", schema="pywarehouse")
