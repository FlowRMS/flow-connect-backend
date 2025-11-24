"""SQLAlchemy ORM model for Jobs entity."""

from datetime import date, datetime
from uuid import UUID

from commons.db.int_enum import IntEnum
from sqlalchemy import Date, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base
from app.graphql.jobs.models.job_status import JobStatus


class Job(Base):
    """
    Job entity representing a job in the CRM system.

    Jobs track work requests with dates, ownership, and status information.
    """

    __tablename__ = "jobs"
    __table_args__ = {"schema": "crm"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    entry_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    job_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[JobStatus] = mapped_column(IntEnum(JobStatus), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requester_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    job_owner_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    def __repr__(self) -> str:
        """String representation of the Job."""
        return (
            f"<Job(id={self.id}, job_name='{self.job_name}', status='{self.status}')>"
        )
