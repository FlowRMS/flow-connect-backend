"""Add takeoffs, takeoff_documents, product_crosses, and cross_prompt_templates tables.

Revision ID: takeoffs_product_crosses_001
Revises: uq_check_details_entities
Create Date: 2026-01-14

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "takeoffs_product_crosses_001"
down_revision: str | None = "uq_check_details_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create takeoffs table
    op.create_table(
        "takeoffs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("takeoff_number", sa.String(20), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(255), nullable=False, server_default="Manual Upload"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("quote_id", sa.UUID(), nullable=True),
        sa.Column("takeoff_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_takeoffs")),
        schema="ai",
    )
    op.create_index("ix_ai_takeoffs_created_by_id", "takeoffs", ["created_by_id"], schema="ai")
    op.create_index("ix_ai_takeoffs_status", "takeoffs", ["status"], schema="ai")
    op.create_index("ix_ai_takeoffs_quote_id", "takeoffs", ["quote_id"], schema="ai")
    op.create_index("ix_ai_takeoffs_takeoff_number", "takeoffs", ["takeoff_number"], unique=True, schema="ai")

    # Create takeoff_documents table
    op.create_table(
        "takeoff_documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("takeoff_id", sa.UUID(), nullable=False),
        sa.Column("file_id", sa.UUID(), nullable=False),
        sa.Column("classification", sa.String(100), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("abridged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("abridged_pages", sa.Integer(), nullable=True),
        sa.Column("abridged_url", sa.TEXT(), nullable=True),
        sa.Column("reduction_percentage", sa.Float(), nullable=True),
        sa.Column("page_analyses", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("products", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("parsed_items", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_takeoff_documents")),
        sa.ForeignKeyConstraint(
            ["takeoff_id"], ["ai.takeoffs.id"],
            name=op.f("fk_ai_takeoff_documents_takeoff_id_takeoffs"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["file_id"], ["pyfiles.files.id"],
            name=op.f("fk_ai_takeoff_documents_file_id_files")
        ),
        schema="ai",
    )
    op.create_index("ix_ai_takeoff_documents_takeoff_id", "takeoff_documents", ["takeoff_id"], schema="ai")
    op.create_index("ix_ai_takeoff_documents_file_id", "takeoff_documents", ["file_id"], schema="ai")
    op.create_index("ix_ai_takeoff_documents_classification", "takeoff_documents", ["classification"], schema="ai")

    # Create product_crosses table
    op.create_table(
        "product_crosses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("competitor_manufacturer", sa.String(255), nullable=False),
        sa.Column("competitor_part_number", sa.String(255), nullable=False),
        sa.Column("competitor_description", sa.String(1000), nullable=True),
        sa.Column("our_manufacturer", sa.String(255), nullable=False),
        sa.Column("our_part_number", sa.String(255), nullable=False),
        sa.Column("our_description", sa.String(1000), nullable=True),
        sa.Column("times_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_used", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_product_crosses")),
        schema="ai",
    )
    op.create_index("ix_ai_product_crosses_user_id", "product_crosses", ["user_id"], schema="ai")
    op.create_index("ix_ai_product_crosses_competitor_manufacturer", "product_crosses", ["competitor_manufacturer"], schema="ai")
    op.create_index("ix_ai_product_crosses_competitor_part_number", "product_crosses", ["competitor_part_number"], schema="ai")
    op.create_index("ix_ai_product_crosses_our_manufacturer", "product_crosses", ["our_manufacturer"], schema="ai")
    op.create_index("ix_ai_product_crosses_our_part_number", "product_crosses", ["our_part_number"], schema="ai")

    # Create cross_prompt_templates table
    op.create_table(
        "cross_prompt_templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("prompt", sa.TEXT(), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("times_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_used", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_cross_prompt_templates")),
        schema="ai",
    )
    op.create_index("ix_ai_cross_prompt_templates_user_id", "cross_prompt_templates", ["user_id"], schema="ai")
    op.create_index("ix_ai_cross_prompt_templates_name", "cross_prompt_templates", ["name"], schema="ai")


def downgrade() -> None:
    op.drop_index("ix_ai_cross_prompt_templates_name", table_name="cross_prompt_templates", schema="ai")
    op.drop_index("ix_ai_cross_prompt_templates_user_id", table_name="cross_prompt_templates", schema="ai")
    op.drop_table("cross_prompt_templates", schema="ai")

    op.drop_index("ix_ai_product_crosses_our_part_number", table_name="product_crosses", schema="ai")
    op.drop_index("ix_ai_product_crosses_our_manufacturer", table_name="product_crosses", schema="ai")
    op.drop_index("ix_ai_product_crosses_competitor_part_number", table_name="product_crosses", schema="ai")
    op.drop_index("ix_ai_product_crosses_competitor_manufacturer", table_name="product_crosses", schema="ai")
    op.drop_index("ix_ai_product_crosses_user_id", table_name="product_crosses", schema="ai")
    op.drop_table("product_crosses", schema="ai")

    op.drop_index("ix_ai_takeoff_documents_classification", table_name="takeoff_documents", schema="ai")
    op.drop_index("ix_ai_takeoff_documents_file_id", table_name="takeoff_documents", schema="ai")
    op.drop_index("ix_ai_takeoff_documents_takeoff_id", table_name="takeoff_documents", schema="ai")
    op.drop_table("takeoff_documents", schema="ai")

    op.drop_index("ix_ai_takeoffs_takeoff_number", table_name="takeoffs", schema="ai")
    op.drop_index("ix_ai_takeoffs_quote_id", table_name="takeoffs", schema="ai")
    op.drop_index("ix_ai_takeoffs_status", table_name="takeoffs", schema="ai")
    op.drop_index("ix_ai_takeoffs_created_by_id", table_name="takeoffs", schema="ai")
    op.drop_table("takeoffs", schema="ai")
