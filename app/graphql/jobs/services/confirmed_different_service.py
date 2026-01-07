import uuid

from commons.auth import AuthInfo
from commons.db.v6.crm.jobs import ConfirmedDifferentJob
from app.graphql.jobs.repositories.confirmed_different_repository import (
    ConfirmedDifferentJobRepository,
)
from app.graphql.jobs.repositories.jobs_repository import JobsRepository


class ConfirmedDifferentService:
    def __init__(
        self,
        repository: ConfirmedDifferentJobRepository,
        jobs_repository: JobsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.jobs_repository = jobs_repository
        self.auth_info = auth_info

    async def confirm_jobs_different(
        self,
        source_job_id: uuid.UUID,
        target_job_id: uuid.UUID,
        reason: str | None = None,
    ) -> ConfirmedDifferentJob:
        source_job = await self.jobs_repository.get_by_id(source_job_id)
        target_job = await self.jobs_repository.get_by_id(target_job_id)

        if not source_job or not target_job:
            raise ValueError("One or both jobs not found")

        if await self.repository.is_confirmed_different(source_job_id, target_job_id):
            raise ValueError("Jobs are already marked as different")

        return await self.repository.create(
            job_id_1=source_job_id,
            job_id_2=target_job_id,
            confirmed_by_id=self.auth_info.flow_user_id,
            reason=reason,
        )

    async def is_confirmed_different(
        self,
        source_job_id: uuid.UUID,
        target_job_id: uuid.UUID,
    ) -> bool:
        return await self.repository.is_confirmed_different(source_job_id, target_job_id)

    async def remove_confirmed_different(
        self,
        source_job_id: uuid.UUID,
        target_job_id: uuid.UUID,
    ) -> bool:
        return await self.repository.delete(source_job_id, target_job_id)

    async def get_confirmed_different_for_job(
        self,
        job_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        return await self.repository.get_confirmed_different_for_job(job_id)
