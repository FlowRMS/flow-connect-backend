"""Strawberry GraphQL response types for Jobs entity."""

from datetime import date, datetime
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.jobs.models.job_status import JobStatus
from app.graphql.jobs.models.jobs_model import Job


@strawberry.type
class JobType(DTOMixin[Job]):
    """
    GraphQL type for Job entity (output/query results).

    Used when returning job data from queries.
    """

    id: UUID
    entry_date: datetime
    created_by: UUID
    status: JobStatus
    job_name: str
    start_date: date | None
    end_date: date | None
    description: str | None
    requester_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Job) -> "JobType":
        """
        Convert ORM model to GraphQL type.

        Args:
            model: The Job ORM model

        Returns:
            JobType instance
        """
        return cls(
            id=model.id,
            entry_date=model.entry_date,
            created_by=model.created_by,
            status=model.status,
            job_name=model.job_name,
            start_date=model.start_date,
            end_date=model.end_date,
            description=model.description,
            requester_id=model.requester_id,
        )
