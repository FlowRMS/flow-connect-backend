"""Strawberry GraphQL input types for Jobs entity."""

from datetime import date
from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.jobs.models.job_status import JobStatus
from app.graphql.jobs.models.jobs_model import Job


@strawberry.input
class JobInput(BaseInputGQL[Job]):
    job_name: str | None = strawberry.UNSET
    start_date: date | None = strawberry.UNSET
    end_date: date | None = strawberry.UNSET
    status: JobStatus | None = strawberry.UNSET
    job_owner_id: UUID | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    requester_id: UUID | None = strawberry.UNSET
    user_owner_ids: list[UUID] | None = strawberry.UNSET

    def to_orm_model(self) -> Job:
        return Job(
            job_name=self.optional_field(self.job_name),
            start_date=self.optional_field(self.start_date),
            end_date=self.optional_field(self.end_date),
            status=self.optional_field(self.status),
            job_owner_id=self.optional_field(self.job_owner_id),
            description=self.optional_field(self.description),
            requester_id=self.optional_field(self.requester_id),
            user_owner_ids=self.optional_field(self.user_owner_ids),
        )
