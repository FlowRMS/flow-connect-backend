"""Strawberry GraphQL response types for Jobs entity."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.jobs.strawberry.status_response import JobStatusType


@strawberry.type
class JobType(DTOMixin[Job]):
    _instance: strawberry.Private[Job]
    id: UUID
    created_at: datetime
    created_by: UUID
    # status: JobStatusType
    job_name: str
    start_date: date | None
    end_date: date | None
    description: str | None
    job_type: str | None
    structural_details: str | None
    structural_information: str | None
    additional_information: str | None
    requester_id: UUID | None
    tags: list[str] | None

    @classmethod
    def from_orm_model(cls, model: Job) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by=model.created_by,
            job_name=model.job_name,
            start_date=model.start_date,
            end_date=model.end_date,
            description=model.description,
            job_type=model.job_type,
            structural_details=model.structural_details,
            structural_information=model.structural_information,
            additional_information=model.additional_information,
            requester_id=model.requester_id,
            tags=model.tags,
        )

    @strawberry.field
    def status(self) -> JobStatusType:
        return JobStatusType.from_orm_model(self._instance.status)
