from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.crm.links.entity_type import EntityType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.inject import inject
from app.graphql.jobs.strawberry.status_response import JobStatusType
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class JobLiteType(DTOMixin[Job]):
    _instance: strawberry.Private[Job]
    id: UUID
    created_at: datetime
    # created_by: UUID
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
            # created_by=model.created_by,
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


@strawberry.type
class JobType(JobLiteType):
    @strawberry.field
    def status(self) -> JobStatusType:
        return JobStatusType.from_orm_model(self._instance.status)

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    @inject
    async def watchers(
        self,
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        users = await watcher_service.get_watchers(EntityType.JOB, self.id)
        return [UserResponse.from_orm_model(u) for u in users]
