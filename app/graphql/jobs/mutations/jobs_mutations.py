"""GraphQL mutations for Jobs entity."""

from uuid import UUID

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

    @strawberry.mutation
    @inject
    async def update_job(
        self,
        id: UUID,
        input: JobInput,
        service: Injected[JobsService],
    ) -> JobType:
        """
        Update an existing job.

        Args:
            id: The job ID to update
            input: The updated job data
            service: Injected JobsService

        Returns:
            The updated JobType object
        """
        return JobType.from_orm_model(await service.update_job(id, input))
