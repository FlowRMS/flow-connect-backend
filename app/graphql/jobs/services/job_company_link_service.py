from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.jobs import JobCompanyLink, JobCompanyRole

from app.errors.common_errors import ConflictError, NotFoundError
from app.graphql.jobs.repositories.job_company_link_repository import (
    JobCompanyLinkRepository,
)


class JobCompanyLinkService:
    def __init__(
        self,
        repository: JobCompanyLinkRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def add_company_to_job(
        self,
        job_id: UUID,
        company_id: UUID,
        role: JobCompanyRole,
    ) -> JobCompanyLink:
        if await self.repository.link_exists(job_id, company_id, role):
            msg = f"Company {company_id} already has role {role.name} on job {job_id}"
            raise ConflictError(msg)

        link = JobCompanyLink(
            job_id=job_id,
            company_id=company_id,
            role=role,
        )
        return await self.repository.create(link)

    async def remove_company_from_job(
        self,
        job_id: UUID,
        company_id: UUID,
        role: JobCompanyRole,
    ) -> bool:
        result = await self.repository.delete_link(job_id, company_id, role)
        if not result:
            msg = f"Link not found for company {company_id} with role {role.name} on job {job_id}"
            raise NotFoundError(msg)
        return result

    async def get_job_companies(self, job_id: UUID) -> list[JobCompanyLink]:
        return await self.repository.get_links_for_job(job_id)

    async def get_specifiers(self, job_id: UUID) -> list[JobCompanyLink]:
        return await self.repository.get_links_by_role(job_id, JobCompanyRole.SPECIFIER)

    async def get_awardees(self, job_id: UUID) -> list[JobCompanyLink]:
        return await self.repository.get_links_by_role(job_id, JobCompanyRole.AWARDEE)
