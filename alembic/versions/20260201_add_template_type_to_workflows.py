from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "add_template_type_001"
down_revision: str | None = "a098b96eeb0f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    template_type_enum = sa.Enum(
        "workflow",
        "pricing_template",
        name="workflow_template_type",
        schema="ai",
    )
    template_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "workflows",
        sa.Column(
            "template_type",
            template_type_enum,
            nullable=False,
            server_default="workflow",
        ),
        schema="ai",
    )


def downgrade() -> None:
    op.drop_column("workflows", "template_type", schema="ai")
    sa.Enum(name="workflow_template_type", schema="ai").drop(
        op.get_bind(), checkfirst=True
    )
