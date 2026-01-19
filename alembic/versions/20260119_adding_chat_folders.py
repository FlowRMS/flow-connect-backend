"""add_chat_folders

Revision ID: e5f6a7b8c9d0
Revises: add_chat_folders
Create Date: 2025-01-15 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_chat_folders"
down_revision: str | None = "job_duplicate_detection_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create chat_folders table
    _ = op.create_table(
        "chat_folders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
            comment="ID of the user who owns this folder",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_chat_folders")),
        schema="ai",
    )
    op.create_index(
        "ix_ai_chat_folders_user_id", "chat_folders", ["user_id"], schema="ai"
    )

    # Add folder_id column to chats table
    op.add_column(
        "chats",
        sa.Column(
            "folder_id",
            sa.UUID(),
            nullable=True,
            comment="ID of the folder this chat belongs to",
        ),
        schema="ai",
    )
    op.create_index("ix_ai_chats_folder_id", "chats", ["folder_id"], schema="ai")
    op.create_foreign_key(
        op.f("fk_ai_chats_folder_id_chat_folders"),
        "chats",
        "chat_folders",
        ["folder_id"],
        ["id"],
        source_schema="ai",
        referent_schema="ai",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Remove folder_id from chats table
    op.drop_constraint(
        op.f("fk_ai_chats_folder_id_chat_folders"),
        "chats",
        schema="ai",
        type_="foreignkey",
    )
    op.drop_index("ix_ai_chats_folder_id", table_name="chats", schema="ai")
    op.drop_column("chats", "folder_id", schema="ai")

    # Drop chat_folders table
    op.drop_index("ix_ai_chat_folders_user_id", table_name="chat_folders", schema="ai")
    op.drop_table("chat_folders", schema="ai")
