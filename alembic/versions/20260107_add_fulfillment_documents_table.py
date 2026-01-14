"""Add fulfillment_documents table.

Revision ID: 20260107_documents
Revises: 20260106_carrier_type
Create Date: 2026-01-07

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260107_documents"
down_revision = "20260106_carrier_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create fulfillment_documents table
    _ = op.create_table(
        "fulfillment_documents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "fulfillment_order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pywarehouse.fulfillment_orders.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column(
            "file_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyfiles.files.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
        ),
        schema="pywarehouse",
    )

    # Create index on fulfillment_order_id for faster queries
    op.create_index(
        "ix_fulfillment_documents_fulfillment_order_id",
        "fulfillment_documents",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Create index on file_id for faster lookups
    op.create_index(
        "ix_fulfillment_documents_file_id",
        "fulfillment_documents",
        ["file_id"],
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fulfillment_documents_fulfillment_order_id",
        table_name="fulfillment_documents",
        schema="pywarehouse",
    )
    op.drop_table("fulfillment_documents", schema="pywarehouse")
