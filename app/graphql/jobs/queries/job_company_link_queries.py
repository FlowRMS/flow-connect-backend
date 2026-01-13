from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.jobs.services.job_company_link_service import JobCompanyLinkService
from app.graphql.jobs.strawberry.job_company_link_response import JobCompanyLinkResponse


@strawberry.type
class JobCompanyLinkQueries:
    @strawberry.field
    @inject
    async def job_company_links(
        self,
        job_id: UUID,
        service: Injected[JobCompanyLinkService],
    ) -> list[JobCompanyLinkResponse]:
        links = await service.get_job_companies(job_id)
        return [JobCompanyLinkResponse.from_orm_model(link) for link in links]

    @strawberry.field
    @inject
    async def job_specifiers(
        self,
        job_id: UUID,
        service: Injected[JobCompanyLinkService],
    ) -> list[JobCompanyLinkResponse]:
        links = await service.get_specifiers(job_id)
        return [JobCompanyLinkResponse.from_orm_model(link) for link in links]

    @strawberry.field
    @inject
    async def job_awardees(
        self,
        job_id: UUID,
        service: Injected[JobCompanyLinkService],
    ) -> list[JobCompanyLinkResponse]:
        links = await service.get_awardees(job_id)
        return [JobCompanyLinkResponse.from_orm_model(link) for link in links]
