from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "add_template_type_001"
down_revision: str | None = "14c956003e6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "workflows",
        sa.Column(
            "template_type",
            sa.String(50),
            nullable=False,
            server_default="workflow",
        ),
        schema="ai",
    )


def downgrade() -> None:
    op.drop_column("workflows", "template_type", schema="ai")
