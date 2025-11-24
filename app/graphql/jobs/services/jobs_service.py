"""Service layer for Jobs entity with business logic."""

from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.jobs.strawberry.job_input import JobInput


class JobsService:
    """
    Service for Jobs entity business logic.

    Handles validation, authorization, and orchestration of job operations.
    """

    def __init__(
        self,
        repository: JobsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def create_job(
        self,
        job_input: JobInput,
    ) -> Job:
        job = job_input.to_orm_model()
        return await self.repository.create(job)

    async def delete_job(self, job_id: UUID | str) -> bool:
        """
        Delete a job.

        Args:
            job_id: The job ID

        Returns:
            True if deleted successfully

        Raises:
            JobNotFoundError: If the job doesn't exist
        """
        if not await self.repository.exists(job_id):
            raise NotFoundError(str(job_id))

        return await self.repository.delete(job_id)

    async def get_job(self, job_id: UUID | str) -> Job:
        """
        Get a job by ID.

        Args:
            job_id: The job ID

        Returns:
            The job entity

        Raises:
            JobNotFoundError: If the job doesn't exist
        """
        job = await self.repository.get_by_id(job_id)
        if not job:
            raise NotFoundError(str(job_id))
        return job
