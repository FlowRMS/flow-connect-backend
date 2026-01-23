"""add custom_instructions table

Revision ID: add_custom_instructions
Revises: warehouse_deliveries_001
Create Date: 2026-01-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_custom_instructions"
down_revision: str | None = "warehouse_deliveries_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "custom_instructions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "level",
            sa.SmallInteger(),
            nullable=False,
            server_default="1",
            comment="Instruction level: 0=ORGANIZATION, 1=USER",
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="User who created the instruction (NULL for org-level)",
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
            comment="Display name for the instruction",
        ),
        sa.Column(
            "instruction",
            sa.Text(),
            nullable=False,
            comment="Natural language instruction text",
        ),
        sa.Column(
            "scope",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="Scope configuration for when instruction fires",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="Whether instruction is enabled",
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Auto-enable for new chats (user-level only)",
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="ai",
    )

    # Create foreign key constraint
    op.create_foreign_key(
        op.f("fk_ai_custom_instructions_user_id_users"),
        "custom_instructions",
        "users",
        ["user_id"],
        ["id"],
        source_schema="ai",
        referent_schema="pyuser",
        ondelete="SET NULL",
    )

    # Create indexes
    op.create_index(
        "ix_ai_custom_instructions_level",
        "custom_instructions",
        ["level"],
        schema="ai",
    )
    op.create_index(
        "ix_ai_custom_instructions_user_id",
        "custom_instructions",
        ["user_id"],
        schema="ai",
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(
        "ix_ai_custom_instructions_user_id",
        table_name="custom_instructions",
        schema="ai",
    )
    op.drop_index(
        "ix_ai_custom_instructions_level",
        table_name="custom_instructions",
        schema="ai",
    )

    # Drop foreign key constraint
    op.drop_constraint(
        op.f("fk_ai_custom_instructions_user_id_users"),
        "custom_instructions",
        schema="ai",
        type_="foreignkey",
    )

    # Drop table
    op.drop_table("custom_instructions", schema="ai")
