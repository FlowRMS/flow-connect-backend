"""Strawberry GraphQL response types for Jobs entity."""

from datetime import date, datetime
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
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
    creation_type: int
    user_owner_ids: list[UUID] | None
    status: str
    is_used: bool
    job_name: str
    start_date: date
    end_date: date
    description: str | None
    requester_id: UUID | None
    job_owner_id: UUID

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
            creation_type=model.creation_type,
            user_owner_ids=model.user_owner_ids,
            status=model.status,
            is_used=model.is_used,
            job_name=model.job_name,
            start_date=model.start_date,
            end_date=model.end_date,
            description=model.description,
            requester_id=model.requester_id,
            job_owner_id=model.job_owner_id,
        )
