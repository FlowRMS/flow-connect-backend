"""SQLAlchemy ORM model for Jobs entity."""

from datetime import date
from uuid import UUID

from commons.db.int_enum import IntEnum
from sqlalchemy import Date, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel, HasCreatedAt, HasCreatedBy, HasPrimaryKey
from app.graphql.jobs.models.job_status import JobStatus


class Job(BaseModel, HasPrimaryKey, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    Job entity representing a job in the CRM system.

    Jobs track work requests with dates, ownership, and status information.
    """

    __tablename__ = "jobs"
    __table_args__ = {"schema": "crm"}

    job_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[JobStatus] = mapped_column(IntEnum(JobStatus), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requester_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    job_owner_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    def __repr__(self) -> str:
        """String representation of the Job."""
        return (
            f"<Job(id={self.id}, job_name='{self.job_name}', status='{self.status}')>"
        )
