"""add factory split rates and factory columns

Revision ID: a1b2c3d4e5f6
Revises: 891079fe3cd6
Create Date: 2025-12-24

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "891079fe3cd6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create pyfiles schema
    op.execute("CREATE SCHEMA IF NOT EXISTS pyfiles;")

    # Create folders table
    _ = op.create_table(
        "folders",
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["pyfiles.folders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pyfiles",
    )

    # Create files table
    _ = op.create_table(
        "files",
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(2000), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_type", sa.SmallInteger(), nullable=True),
        sa.Column("file_sha", sa.String(64), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("folder_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["folder_id"],
            ["pyfiles.folders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pyfiles",
    )
    op.create_index(
        op.f("ix_pyfiles_files_folder_id"),
        "files",
        ["folder_id"],
        unique=False,
        schema="pyfiles",
    )

    # Add new columns to factories table
    op.add_column(
        "factories",
        sa.Column("account_number", sa.String(255), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("email", sa.String(255), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("phone", sa.String(50), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("logo_id", sa.UUID(), nullable=True),
        schema="pycore",
    )
    op.create_foreign_key(
        "fk_factories_logo_id_files",
        "factories",
        "files",
        ["logo_id"],
        ["id"],
        source_schema="pycore",
        referent_schema="pyfiles",
    )
    op.add_column(
        "factories",
        sa.Column("lead_time", sa.Integer(), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("payment_terms", sa.Integer(), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column(
            "base_commission_rate",
            sa.Numeric(5, 2),
            server_default="0",
            nullable=False,
        ),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column(
            "commission_discount_rate",
            sa.Numeric(5, 2),
            server_default="0",
            nullable=False,
        ),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column(
            "overall_discount_rate",
            sa.Numeric(5, 2),
            server_default="0",
            nullable=False,
        ),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("additional_information", sa.Text(), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("freight_terms", sa.Text(), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("external_payment_terms", sa.Text(), nullable=True),
        schema="pycore",
    )

    # Create factory_split_rates table
    _ = op.create_table(
        "factory_split_rates",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("factory_id", sa.UUID(), nullable=False),
        sa.Column("split_rate", sa.Numeric(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycore",
    )
    op.create_index(
        op.f("ix_pycore_factory_split_rates_factory_id"),
        "factory_split_rates",
        ["factory_id"],
        unique=False,
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_pycore_factory_split_rates_factory_id"),
        table_name="factory_split_rates",
        schema="pycore",
    )
    op.drop_table("factory_split_rates", schema="pycore")

    # Drop added columns from factories table
    op.drop_column("factories", "external_payment_terms", schema="pycore")
    op.drop_column("factories", "freight_terms", schema="pycore")
    op.drop_column("factories", "additional_information", schema="pycore")
    op.drop_column("factories", "overall_discount_rate", schema="pycore")
    op.drop_column("factories", "commission_discount_rate", schema="pycore")
    op.drop_column("factories", "base_commission_rate", schema="pycore")
    op.drop_column("factories", "payment_terms", schema="pycore")
    op.drop_column("factories", "lead_time", schema="pycore")
    op.drop_constraint(
        "fk_factories_logo_id_files", "factories", schema="pycore", type_="foreignkey"
    )
    op.drop_column("factories", "logo_id", schema="pycore")
    op.drop_column("factories", "phone", schema="pycore")
    op.drop_column("factories", "email", schema="pycore")
    op.drop_column("factories", "account_number", schema="pycore")

    # Drop files and folders tables
    op.drop_index(
        op.f("ix_pyfiles_files_folder_id"),
        table_name="files",
        schema="pyfiles",
    )
    op.drop_table("files", schema="pyfiles")
    op.drop_table("folders", schema="pyfiles")
