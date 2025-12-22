"""Service layer for JobStatus entity with business logic."""

from commons.auth import AuthInfo
from commons.db.v6.crm.jobs.job_status_model import JobStatus

from app.graphql.jobs.repositories.status_repository import JobStatusRepository


class JobStatusService:
    """
    Service for JobStatus entity business logic.

    Handles validation, authorization, and orchestration of job status operations.
    """

    def __init__(
        self,
        repository: JobStatusRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_all_statuses(
        self,
    ) -> list[JobStatus]:
        return await self.repository.list_all(limit=None, offset=0)
