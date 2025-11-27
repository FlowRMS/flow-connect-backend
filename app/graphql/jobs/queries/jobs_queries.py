"""GraphQL queries for Jobs entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.jobs.services.status_service import JobStatusService
from app.graphql.jobs.strawberry.job_response import JobType
from app.graphql.jobs.strawberry.status_response import JobStatusType


@strawberry.type
class JobsQueries:
    """GraphQL queries for Jobs entity."""

    @strawberry.field
    @inject
    async def job(
        self,
        id: UUID,
        service: Injected[JobsService],
    ) -> JobType:
        return JobType.from_orm_model(await service.get_job(id))

    @strawberry.field
    @inject
    async def job_statuses(
        self,
        service: Injected[JobStatusService],
    ) -> list[JobStatusType]:
        return JobStatusType.from_orm_model_list(await service.get_all_statuses())
