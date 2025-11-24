"""GraphQL mutations for Jobs entity."""

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.jobs.strawberry.job_input import JobInput
from app.graphql.jobs.strawberry.job_response import JobType


@strawberry.type
class JobsMutations:
    """GraphQL mutations for Jobs entity."""

    @strawberry.mutation
    @inject
    async def create_job(
        self,
        input: JobInput,
        service: Injected[JobsService],
    ) -> JobType:
        return JobType.from_orm_model(await service.create_job(job_input=input))
