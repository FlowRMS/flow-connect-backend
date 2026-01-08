from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "71ad17a08c48"
down_revision: str | None = "06f9eafc78e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "pending_document_processings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pending_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.pending_documents.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "entity_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            index=True,
            comment="The ID of the created entity, if successful",
        ),
        sa.Column(
            "status",
            sa.SmallInteger(),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "dto_json",
            postgresql.JSONB(),
            nullable=True,
            comment="The DTO data that was processed",
        ),
        sa.Column(
            "error_message",
            sa.String(),
            nullable=True,
            comment="Error message if processing failed",
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )


def downgrade() -> None:
    op.drop_table("pending_document_processings", schema="ai")
