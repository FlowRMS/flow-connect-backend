"""adding ai models

Revision ID: 9d87acc00979
Revises: cd1f6cbd8751
Create Date: 2025-12-28 20:03:23.275621

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "9d87acc00979"
down_revision: str | None = "cd1f6cbd8751"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS ai")

    # Chat tables
    _ = op.create_table(
        "chats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("session_id", sa.String(255), nullable=True, index=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, default=1),
        sa.Column(
            "follow_up_suggestions", postgresql.ARRAY(sa.String()), nullable=True
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role", sa.SmallInteger(), nullable=False),
        sa.Column("message_type", sa.SmallInteger(), nullable=False, default=1),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tool_name", sa.String(100), nullable=True),
        sa.Column("tool_args", postgresql.JSONB(), nullable=True),
        sa.Column("meta_data", postgresql.JSONB(), nullable=True),
        sa.Column(
            "chat_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.chats.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "chat_message_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("feedback_type", sa.SmallInteger(), nullable=False),
        sa.Column(
            "message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.chat_messages.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("feedback_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    # Document cluster tables
    _ = op.create_table(
        "document_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cluster_name", sa.String(500), nullable=False),
        sa.Column("cluster_metadata", postgresql.JSONB(), nullable=True),
        sa.Column(
            "is_hidden",
            sa.Boolean(),
            nullable=False,
            default=False,
            server_default="FALSE",
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "cluster_contexts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "cluster_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.document_clusters.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "file_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyfiles.files.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("converted_text_content", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    # Pending document tables
    _ = op.create_table(
        "pending_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "file_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyfiles.files.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "cluster_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.document_clusters.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("original_presigned_url", sa.String(), nullable=False),
        sa.Column("document_type", sa.SmallInteger(), nullable=False),
        sa.Column("workflow_status", sa.SmallInteger(), nullable=True),
        sa.Column("document_sample_content", sa.String(), nullable=False),
        sa.Column("entity_type", sa.SmallInteger(), nullable=True, index=True),
        sa.Column("source_type", sa.SmallInteger(), nullable=True),
        sa.Column("source_name", sa.String(500), nullable=True),
        sa.Column("similar_documents_json", postgresql.JSONB(), nullable=True),
        sa.Column("extracted_data_json", postgresql.JSONB(), nullable=True),
        sa.Column("converted_document_url", sa.String(), nullable=True),
        sa.Column(
            "file_upload_process_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            unique=True,
        ),
        sa.Column(
            "additional_instructions_json",
            postgresql.JSONB(),
            nullable=False,
            default=[],
        ),
        sa.Column("source_classification_json", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, index=True),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("sha", sa.String(), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=True, default=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "pending_document_pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pending_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.pending_documents.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("markdown_content", sa.Text(), nullable=False),
        sa.Column("entity_number", sa.String(255), nullable=True),
        sa.Column("page_type", sa.SmallInteger(), nullable=False),
        sa.Column(
            "is_relevant_for_transactions", sa.Boolean(), nullable=False, default=False
        ),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("number_of_detail_lines", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "pending_document_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pending_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.pending_documents.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column("entity_type", sa.SmallInteger(), nullable=False, index=True),
        sa.Column("action", sa.SmallInteger(), nullable=False, index=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "pending_document_correction_changes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pending_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.pending_documents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("correction_action", sa.String(255), nullable=False),
        sa.Column("old_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "extracted_data_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pending_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.pending_documents.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("data", postgresql.JSONB(), nullable=True),
        sa.Column("change_description", sa.String(500), nullable=False),
        sa.Column("change_type", sa.SmallInteger(), nullable=False),
        sa.Column("user_instruction", sa.Text(), nullable=True),
        sa.Column("executed_code", sa.Text(), nullable=True),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=True,
        ),
        sa.Column("meta_data", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )
    op.create_index(
        "ix_extracted_data_versions_pending_document_id_version",
        "extracted_data_versions",
        ["pending_document_id", "version_number"],
        unique=True,
        schema="ai",
    )

    # Pending entity tables
    _ = op.create_table(
        "pending_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.SmallInteger(), nullable=False, index=True),
        sa.Column("confirmation_status", sa.SmallInteger(), nullable=False, index=True),
        sa.Column(
            "pending_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.pending_documents.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "dto_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True
        ),
        sa.Column("flow_index_detail", sa.Integer(), nullable=True),
        sa.Column("extracted_data", postgresql.JSONB(), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("source_line_numbers", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("best_match_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("best_match_name", sa.String(), nullable=True),
        sa.Column(
            "best_match_similarity", sa.DECIMAL(precision=5, scale=4), nullable=True
        ),
        sa.Column("confirmed_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "confirmed_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "entity_match_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pending_entity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.pending_entities.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("existing_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("existing_entity_name", sa.String(255), nullable=False),
        sa.Column("similarity_score", sa.DECIMAL(precision=5, scale=4), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("match_metadata", postgresql.JSONB(), nullable=True),
        schema="ai",
    )
    op.create_unique_constraint(
        "uq_match_candidate_entity",
        "entity_match_candidates",
        ["pending_entity_id", "existing_entity_id"],
        schema="ai",
    )
    op.create_unique_constraint(
        "uq_match_candidate_rank",
        "entity_match_candidates",
        ["pending_entity_id", "rank"],
        schema="ai",
    )

    # Email tables
    _ = op.create_table(
        "emails",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "external_id", sa.String(255), nullable=False, unique=True, index=True
        ),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("conversation_id", sa.String(255), nullable=False, index=True),
        sa.Column("from_email", sa.String(255), nullable=False, index=True),
        sa.Column("to_email", sa.String(255), nullable=False, index=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("status", sa.SmallInteger(), nullable=False, index=True),
        sa.Column("category", sa.String(100), nullable=True, index=True),
        sa.Column("urgency", sa.String(50), nullable=True, index=True),
        sa.Column("sentiment", sa.String(50), nullable=True),
        sa.Column("classification_confidence", sa.Float(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("requires_response", sa.Boolean(), nullable=True),
        sa.Column("suggested_actions", postgresql.JSONB(), nullable=True),
        sa.Column("extracted_entities", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "email_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "email_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.emails.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(255), nullable=True),
        sa.Column("size", sa.Integer(), nullable=True),
        sa.Column("s3_key", sa.String(1000), nullable=True),
        sa.Column("document_type", sa.String(100), nullable=True, index=True),
        sa.Column("classification_confidence", sa.Float(), nullable=True),
        sa.Column("document_description", sa.Text(), nullable=True),
        sa.Column("extracted_metadata", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    # Workflow tables
    _ = op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("workflow_json", postgresql.JSON(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, default="draft"),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=True,
        ),
        sa.Column("is_public", sa.Boolean(), nullable=False, default=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("generated_code", sa.Text(), nullable=True),
        sa.Column("pseudo_code", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "workflow_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.workflows.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        sa.Column("input_data", postgresql.JSONB(), nullable=True),
        sa.Column("output_data", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("execution_log", sa.Text(), nullable=True),
        sa.Column("started_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="ai",
    )

    _ = op.create_table(
        "workflow_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai.workflows.id"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column(
            "uploaded_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("file_type", sa.String(100), nullable=True),
        schema="ai",
    )


def downgrade() -> None:
    # Workflow tables
    op.drop_table("workflow_files", schema="ai")
    op.drop_table("workflow_executions", schema="ai")
    op.drop_table("workflows", schema="ai")

    # Email tables
    op.drop_table("email_attachments", schema="ai")
    op.drop_table("emails", schema="ai")

    # Entity tables
    op.drop_constraint(
        "uq_match_candidate_rank", "entity_match_candidates", schema="ai"
    )
    op.drop_constraint(
        "uq_match_candidate_entity", "entity_match_candidates", schema="ai"
    )
    op.drop_table("entity_match_candidates", schema="ai")
    op.drop_table("pending_entities", schema="ai")

    # Document tables
    op.drop_index(
        "ix_extracted_data_versions_pending_document_id_version",
        table_name="extracted_data_versions",
        schema="ai",
    )
    op.drop_table("extracted_data_versions", schema="ai")
    op.drop_table("pending_document_correction_changes", schema="ai")
    op.drop_table("pending_document_entities", schema="ai")
    op.drop_table("pending_document_pages", schema="ai")
    op.drop_table("pending_documents", schema="ai")

    # Cluster tables
    op.drop_table("cluster_contexts", schema="ai")
    op.drop_table("document_clusters", schema="ai")

    # Chat tables
    op.drop_table("chat_message_feedback", schema="ai")
    op.drop_table("chat_messages", schema="ai")
    op.drop_table("chats", schema="ai")

    op.execute("DROP SCHEMA IF EXISTS ai")
