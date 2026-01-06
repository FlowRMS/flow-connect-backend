import uuid
from datetime import datetime

from commons.db.v6.base import HasCreatedAt, PyCRMBaseModel
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.user import User
from sqlalchemy import CheckConstraint, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ConfirmedDifferentJob(PyCRMBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "confirmed_different_jobs"
    __table_args__ = (
        UniqueConstraint("job_id_1", "job_id_2", name="uq_confirmed_different_jobs"),
        CheckConstraint("job_id_1 < job_id_2", name="ck_job_id_ordering"),
        {"schema": "pycrm"},
    )

    job_id_1: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id_2: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    confirmed_by_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pyuser.users.id"),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )

    confirmed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),
    )

    job_1: Mapped[Job] = relationship(
        init=False,
        lazy="joined",
        foreign_keys=[job_id_1],
    )

    job_2: Mapped[Job] = relationship(
        init=False,
        lazy="joined",
        foreign_keys=[job_id_2],
    )

    confirmed_by: Mapped[User] = relationship(
        init=False,
        lazy="joined",
    )
