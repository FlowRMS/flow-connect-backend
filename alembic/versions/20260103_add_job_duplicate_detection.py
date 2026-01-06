"""Add job duplicate detection tables

Revision ID: job_duplicate_detection_001
Revises: order_acknowledgements_001
Create Date: 2026-01-03

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "job_duplicate_detection_001"
down_revision: str | None = "order_acknowledgements_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "job_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding_version", sa.String(50), nullable=False),
        sa.Column("text_hash", sa.String(64), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["pycrm.jobs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
        schema="pycrm",
    )

    op.create_index(
        "ix_pycrm_job_embeddings_job_id",
        "job_embeddings",
        ["job_id"],
        schema="pycrm",
    )

    _ = op.create_table(
        "confirmed_different_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id_1", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id_2", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("confirmed_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "confirmed_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["job_id_1"],
            ["pycrm.jobs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id_2"],
            ["pycrm.jobs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["confirmed_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id_1", "job_id_2", name="uq_confirmed_different_jobs"),
        sa.CheckConstraint("job_id_1 < job_id_2", name="ck_job_id_ordering"),
        schema="pycrm",
    )

    op.create_index(
        "ix_pycrm_confirmed_different_jobs_job_id_1",
        "confirmed_different_jobs",
        ["job_id_1"],
        schema="pycrm",
    )

    op.create_index(
        "ix_pycrm_confirmed_different_jobs_job_id_2",
        "confirmed_different_jobs",
        ["job_id_2"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_pycrm_confirmed_different_jobs_job_id_2",
        table_name="confirmed_different_jobs",
        schema="pycrm",
    )
    op.drop_index(
        "ix_pycrm_confirmed_different_jobs_job_id_1",
        table_name="confirmed_different_jobs",
        schema="pycrm",
    )
    op.drop_table("confirmed_different_jobs", schema="pycrm")
    op.drop_index(
        "ix_pycrm_job_embeddings_job_id",
        table_name="job_embeddings",
        schema="pycrm",
    )
    op.drop_table("job_embeddings", schema="pycrm")
