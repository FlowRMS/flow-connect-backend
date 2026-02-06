"""Create connect_geography schema with countries and subdivisions tables

Revision ID: 20260127_001
Revises: 20260123_001
Create Date: 2026-01-27 09:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260127_001"
down_revision: str | None = "20260126_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

USA_COUNTRY_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

US_SUBDIVISIONS = [
    ("Alabama", "US-AL"),
    ("Alaska", "US-AK"),
    ("Arizona", "US-AZ"),
    ("Arkansas", "US-AR"),
    ("California", "US-CA"),
    ("Colorado", "US-CO"),
    ("Connecticut", "US-CT"),
    ("Delaware", "US-DE"),
    ("District of Columbia", "US-DC"),
    ("Florida", "US-FL"),
    ("Georgia", "US-GA"),
    ("Hawaii", "US-HI"),
    ("Idaho", "US-ID"),
    ("Illinois", "US-IL"),
    ("Indiana", "US-IN"),
    ("Iowa", "US-IA"),
    ("Kansas", "US-KS"),
    ("Kentucky", "US-KY"),
    ("Louisiana", "US-LA"),
    ("Maine", "US-ME"),
    ("Maryland", "US-MD"),
    ("Massachusetts", "US-MA"),
    ("Michigan", "US-MI"),
    ("Minnesota", "US-MN"),
    ("Mississippi", "US-MS"),
    ("Missouri", "US-MO"),
    ("Montana", "US-MT"),
    ("Nebraska", "US-NE"),
    ("Nevada", "US-NV"),
    ("New Hampshire", "US-NH"),
    ("New Jersey", "US-NJ"),
    ("New Mexico", "US-NM"),
    ("New York", "US-NY"),
    ("North Carolina", "US-NC"),
    ("North Dakota", "US-ND"),
    ("Ohio", "US-OH"),
    ("Oklahoma", "US-OK"),
    ("Oregon", "US-OR"),
    ("Pennsylvania", "US-PA"),
    ("Rhode Island", "US-RI"),
    ("South Carolina", "US-SC"),
    ("South Dakota", "US-SD"),
    ("Tennessee", "US-TN"),
    ("Texas", "US-TX"),
    ("Utah", "US-UT"),
    ("Vermont", "US-VT"),
    ("Virginia", "US-VA"),
    ("Washington", "US-WA"),
    ("West Virginia", "US-WV"),
    ("Wisconsin", "US-WI"),
    ("Wyoming", "US-WY"),
]


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS connect_geography")

    op.create_table(
        "countries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(3), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_countries_name"),
        sa.UniqueConstraint("code", name="uq_countries_code"),
        schema="connect_geography",
    )

    op.create_table(
        "subdivisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("iso_code", sa.String(10), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["country_id"],
            ["connect_geography.countries.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("iso_code", name="uq_subdivisions_iso_code"),
        schema="connect_geography",
    )

    op.create_index(
        "ix_subdivisions_country_id",
        "subdivisions",
        ["country_id"],
        schema="connect_geography",
    )

    # Seed USA country
    op.execute(
        f"""
        INSERT INTO connect_geography.countries (id, name, code)
        VALUES ('{USA_COUNTRY_ID}', 'United States of America', 'USA')
        """
    )

    # Seed US subdivisions
    for name, iso_code in US_SUBDIVISIONS:
        op.execute(
            f"""
            INSERT INTO connect_geography.subdivisions (id, country_id, name, iso_code)
            VALUES (gen_random_uuid(), '{USA_COUNTRY_ID}', '{name}', '{iso_code}')
            """
        )


def downgrade() -> None:
    op.drop_index(
        "ix_subdivisions_country_id",
        table_name="subdivisions",
        schema="connect_geography",
    )
    op.drop_table("subdivisions", schema="connect_geography")
    op.drop_table("countries", schema="connect_geography")
    op.execute("DROP SCHEMA IF EXISTS connect_geography")
