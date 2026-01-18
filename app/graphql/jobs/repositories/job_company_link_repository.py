from uuid import UUID

from commons.db.v6.crm.jobs import JobCompanyLink, JobCompanyRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class JobCompanyLinkRepository(BaseRepository[JobCompanyLink]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, JobCompanyLink)

    async def get_by_id_with_company(self, link_id: UUID) -> JobCompanyLink | None:
        stmt = (
            select(JobCompanyLink)
            .where(JobCompanyLink.id == link_id)
            .options(joinedload(JobCompanyLink.company))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_links_for_job(self, job_id: UUID) -> list[JobCompanyLink]:
        stmt = (
            select(JobCompanyLink)
            .where(JobCompanyLink.job_id == job_id)
            .options(joinedload(JobCompanyLink.company))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_links_by_role(
        self, job_id: UUID, role: JobCompanyRole
    ) -> list[JobCompanyLink]:
        stmt = (
            select(JobCompanyLink)
            .where(JobCompanyLink.job_id == job_id, JobCompanyLink.role == role)
            .options(joinedload(JobCompanyLink.company))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def link_exists(
        self, job_id: UUID, company_id: UUID, role: JobCompanyRole
    ) -> bool:
        stmt = select(JobCompanyLink).where(
            JobCompanyLink.job_id == job_id,
            JobCompanyLink.company_id == company_id,
            JobCompanyLink.role == role,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_link(
        self, job_id: UUID, company_id: UUID, role: JobCompanyRole
    ) -> bool:
        stmt = select(JobCompanyLink).where(
            JobCompanyLink.job_id == job_id,
            JobCompanyLink.company_id == company_id,
            JobCompanyLink.role == role,
        )
        result = await self.session.execute(stmt)
        link = result.scalar_one_or_none()

        if link is None:
            return False

        return await self.delete(link.id)
