"""update foreign keys to reference user tables

Revision ID: f6e5d4c3b2a1
Revises: 23c443a27ef7
Create Date: 2025-12-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f6e5d4c3b2a1"
down_revision: str | None = "23c443a27ef7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Clear existing data that references old base tables
    # Since we can't map old IDs to new user-specific IDs, we need to clear the data
    # Users will need to recreate their notes/tasks/etc. using the new user-specific IDs
    op.execute(sa.text("DELETE FROM report.nemra_notes"))
    op.execute(sa.text("DELETE FROM report.nemra_tasks"))
    op.execute(sa.text("DELETE FROM report.nemra_discussions"))
    op.execute(sa.text("DELETE FROM report.strategic_action_responses"))
    op.execute(sa.text("DELETE FROM report.strategic_actions"))
    op.execute(sa.text("DELETE FROM report.strategic_ask_responses"))
    op.execute(sa.text("DELETE FROM report.strategic_ask"))

    # Drop old foreign keys and indexes
    # nemra_notes
    op.drop_constraint(
        "nemra_notes_page_id_fkey", "nemra_notes", schema="report", type_="foreignkey"
    )
    op.drop_constraint(
        "nemra_notes_module_id_fkey", "nemra_notes", schema="report", type_="foreignkey"
    )

    # nemra_tasks
    op.drop_constraint(
        "nemra_tasks_page_id_fkey", "nemra_tasks", schema="report", type_="foreignkey"
    )
    op.drop_constraint(
        "nemra_tasks_module_id_fkey", "nemra_tasks", schema="report", type_="foreignkey"
    )

    # nemra_discussions
    op.drop_constraint(
        "nemra_discussions_page_id_fkey",
        "nemra_discussions",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "nemra_discussions_module_id_fkey",
        "nemra_discussions",
        schema="report",
        type_="foreignkey",
    )

    # strategic_actions
    op.drop_constraint(
        "strategic_actions_page_id_fkey",
        "strategic_actions",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_actions_module_id_fkey",
        "strategic_actions",
        schema="report",
        type_="foreignkey",
    )

    # strategic_action_responses
    op.drop_constraint(
        "strategic_action_responses_page_id_fkey",
        "strategic_action_responses",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_action_responses_module_id_fkey",
        "strategic_action_responses",
        schema="report",
        type_="foreignkey",
    )

    # strategic_ask
    op.drop_constraint(
        "strategic_ask_page_id_fkey",
        "strategic_ask",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_ask_module_id_fkey",
        "strategic_ask",
        schema="report",
        type_="foreignkey",
    )

    # strategic_ask_responses
    op.drop_constraint(
        "strategic_ask_responses_page_id_fkey",
        "strategic_ask_responses",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_ask_responses_module_id_fkey",
        "strategic_ask_responses",
        schema="report",
        type_="foreignkey",
    )

    # Add new foreign keys to user tables
    # nemra_notes
    op.create_foreign_key(
        "nemra_notes_page_id_fkey",
        "nemra_notes",
        "nemra_user_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "nemra_notes_module_id_fkey",
        "nemra_notes",
        "nemra_user_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # nemra_tasks
    op.create_foreign_key(
        "nemra_tasks_page_id_fkey",
        "nemra_tasks",
        "nemra_user_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "nemra_tasks_module_id_fkey",
        "nemra_tasks",
        "nemra_user_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # nemra_discussions
    op.create_foreign_key(
        "nemra_discussions_page_id_fkey",
        "nemra_discussions",
        "nemra_user_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "nemra_discussions_module_id_fkey",
        "nemra_discussions",
        "nemra_user_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_actions
    op.create_foreign_key(
        "strategic_actions_page_id_fkey",
        "strategic_actions",
        "nemra_user_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_actions_module_id_fkey",
        "strategic_actions",
        "nemra_user_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_action_responses
    op.create_foreign_key(
        "strategic_action_responses_page_id_fkey",
        "strategic_action_responses",
        "nemra_user_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_action_responses_module_id_fkey",
        "strategic_action_responses",
        "nemra_user_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_ask
    op.create_foreign_key(
        "strategic_ask_page_id_fkey",
        "strategic_ask",
        "nemra_user_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_ask_module_id_fkey",
        "strategic_ask",
        "nemra_user_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_ask_responses
    op.create_foreign_key(
        "strategic_ask_responses_page_id_fkey",
        "strategic_ask_responses",
        "nemra_user_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_ask_responses_module_id_fkey",
        "strategic_ask_responses",
        "nemra_user_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Drop new foreign keys
    # nemra_notes
    op.drop_constraint(
        "nemra_notes_page_id_fkey", "nemra_notes", schema="report", type_="foreignkey"
    )
    op.drop_constraint(
        "nemra_notes_module_id_fkey", "nemra_notes", schema="report", type_="foreignkey"
    )

    # nemra_tasks
    op.drop_constraint(
        "nemra_tasks_page_id_fkey", "nemra_tasks", schema="report", type_="foreignkey"
    )
    op.drop_constraint(
        "nemra_tasks_module_id_fkey", "nemra_tasks", schema="report", type_="foreignkey"
    )

    # nemra_discussions
    op.drop_constraint(
        "nemra_discussions_page_id_fkey",
        "nemra_discussions",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "nemra_discussions_module_id_fkey",
        "nemra_discussions",
        schema="report",
        type_="foreignkey",
    )

    # strategic_actions
    op.drop_constraint(
        "strategic_actions_page_id_fkey",
        "strategic_actions",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_actions_module_id_fkey",
        "strategic_actions",
        schema="report",
        type_="foreignkey",
    )

    # strategic_action_responses
    op.drop_constraint(
        "strategic_action_responses_page_id_fkey",
        "strategic_action_responses",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_action_responses_module_id_fkey",
        "strategic_action_responses",
        schema="report",
        type_="foreignkey",
    )

    # strategic_ask
    op.drop_constraint(
        "strategic_ask_page_id_fkey",
        "strategic_ask",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_ask_module_id_fkey",
        "strategic_ask",
        schema="report",
        type_="foreignkey",
    )

    # strategic_ask_responses
    op.drop_constraint(
        "strategic_ask_responses_page_id_fkey",
        "strategic_ask_responses",
        schema="report",
        type_="foreignkey",
    )
    op.drop_constraint(
        "strategic_ask_responses_module_id_fkey",
        "strategic_ask_responses",
        schema="report",
        type_="foreignkey",
    )

    # Re-add old foreign keys to base tables
    # nemra_notes
    op.create_foreign_key(
        "nemra_notes_page_id_fkey",
        "nemra_notes",
        "nemra_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "nemra_notes_module_id_fkey",
        "nemra_notes",
        "nemra_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # nemra_tasks
    op.create_foreign_key(
        "nemra_tasks_page_id_fkey",
        "nemra_tasks",
        "nemra_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "nemra_tasks_module_id_fkey",
        "nemra_tasks",
        "nemra_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # nemra_discussions
    op.create_foreign_key(
        "nemra_discussions_page_id_fkey",
        "nemra_discussions",
        "nemra_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "nemra_discussions_module_id_fkey",
        "nemra_discussions",
        "nemra_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_actions
    op.create_foreign_key(
        "strategic_actions_page_id_fkey",
        "strategic_actions",
        "nemra_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_actions_module_id_fkey",
        "strategic_actions",
        "nemra_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_action_responses
    op.create_foreign_key(
        "strategic_action_responses_page_id_fkey",
        "strategic_action_responses",
        "nemra_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_action_responses_module_id_fkey",
        "strategic_action_responses",
        "nemra_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_ask
    op.create_foreign_key(
        "strategic_ask_page_id_fkey",
        "strategic_ask",
        "nemra_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_ask_module_id_fkey",
        "strategic_ask",
        "nemra_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )

    # strategic_ask_responses
    op.create_foreign_key(
        "strategic_ask_responses_page_id_fkey",
        "strategic_ask_responses",
        "nemra_pages",
        ["page_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategic_ask_responses_module_id_fkey",
        "strategic_ask_responses",
        "nemra_modules",
        ["module_id"],
        ["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
