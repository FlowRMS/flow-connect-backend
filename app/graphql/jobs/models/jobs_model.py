"""SQLAlchemy ORM model for Jobs entity."""

import uuid
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import BaseModel, HasCreatedAt, HasCreatedBy, HasPrimaryKey

if TYPE_CHECKING:
    from app.graphql.jobs.models.status_model import JobStatus


class Job(BaseModel, HasPrimaryKey, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    Job entity representing a job in the CRM system.

    Jobs track work requests with dates, ownership, and status information.
    """

    __tablename__ = "jobs"
    __table_args__ = {"schema": "crm"}

    job_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("crm.job_statuses.id"), nullable=False
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    job_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    structural_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    structural_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    additional_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requester_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    job_owner_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    status: Mapped["JobStatus"] = relationship(
        init=False, back_populates="jobs", lazy="joined"
    )

    def __repr__(self) -> str:
        """String representation of the Job."""
        return f"<Job(id={self.id}, job_name='{self.job_name}', status_id={self.status_id})>"
