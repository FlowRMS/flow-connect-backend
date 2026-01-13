"""Insert default job statuses

Revision ID: insert_default_job_statuses
Revises: add_buying_group
Create Date: 2026-01-12

"""

from collections.abc import Sequence

from alembic import op

revision: str = "insert_default_job_statuses"
down_revision: str | None = "add_buying_group"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_JOB_STATUSES = [
    "Closed",
    "BID",
    "In Progress",
    "Open",
]


def upgrade() -> None:
    for name in DEFAULT_JOB_STATUSES:
        op.execute(f"""
            INSERT INTO pycrm.job_statuses (id, name)
            VALUES (gen_random_uuid(), '{name}')
            ON CONFLICT (name) DO NOTHING;
        """)


def downgrade() -> None:
    pass
