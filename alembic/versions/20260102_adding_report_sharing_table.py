"""adding_report_sharing_table

Revision ID: add_report_sharing_table
Revises: add_sidebar_configurations
Create Date: 2026-01-02 16:59:25.626923

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_report_sharing_table"
down_revision: str | None = "add_sidebar_configurations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "shared_templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("report_template_id", sa.UUID(), nullable=False),
        sa.Column("shared_with_user_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="report",
    )
    # indexes for report_template_id and shared_with_user_id
    _ = op.create_index(
        "idx_shared_templates_report_template_id",
        "shared_templates",
        ["report_template_id"],
        schema="report",
    )
    _ = op.create_index(
        "idx_shared_templates_shared_with_user_id",
        "shared_templates",
        ["shared_with_user_id"],
        schema="report",
    )
    # foreign key for report_template_id - fix: the table name must be without schema prefix
    _ = op.create_foreign_key(
        "fk_shared_templates_report_template_id",
        source_table="shared_templates",
        referent_table="report_templates",
        local_cols=["report_template_id"],
        remote_cols=["id"],
        source_schema="report",
        referent_schema="report",
        ondelete="CASCADE",
    )
    _ = op.create_foreign_key(
        "fk_shared_templates_shared_with_user_id",
        source_table="shared_templates",
        referent_table="users",
        local_cols=["shared_with_user_id"],
        remote_cols=["id"],
        source_schema="report",
        referent_schema="pyuser",
        ondelete="CASCADE",
    )

    _ = op.add_column(
        "report_templates",
        sa.Column(
            "organization_shared",
            sa.Boolean(),
            nullable=True,
            server_default=sa.false(),
        ),
        schema="report",
    )

    _ = op.execute("UPDATE report.report_templates SET organization_shared = FALSE")
    _ = op.alter_column(
        "report_templates", "organization_shared", nullable=False, schema="report"
    )

    # constraint unique on report_template_id and shared_with_user_id combination
    _ = op.create_unique_constraint(
        "uq_shared_templates_report_template_id_shared_with_user_id",
        "shared_templates",
        ["report_template_id", "shared_with_user_id"],
        schema="report",
    )

    # add report template created_at server default now
    _ = op.alter_column(
        "report_templates",
        "created_at",
        server_default=sa.text("now()"),
        schema="report",
    )
    # add foreign key for user_id at report_templates table
    _ = op.create_foreign_key(
        "fk_report_templates_user_id",
        source_table="report_templates",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        source_schema="report",
        referent_schema="pyuser",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    _ = op.drop_column("report_templates", "organization_shared", schema="report")
    _ = op.drop_table("shared_templates", schema="report")
    _ = op.alter_column(
        "report_templates", "created_at", server_default=None, schema="report"
    )
    _ = op.drop_constraint(
        "fk_report_templates_user_id",
        "report_templates",
        schema="report",
        type_="foreignkey",
    )
