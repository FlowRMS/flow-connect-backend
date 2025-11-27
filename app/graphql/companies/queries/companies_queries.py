from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.inject import inject


@strawberry.type
class CompaniesQueries:
    @strawberry.field
    @inject
    async def company(
        self,
        id: UUID,
        service: Injected[CompaniesService],
    ) -> CompanyResponse:
        return CompanyResponse.from_orm_model(await service.get_company(id))

    @strawberry.field
    @inject
    async def companies(
        self,
        service: Injected[CompaniesService],
        limit: int = 100,
        offset: int = 0,
    ) -> list[CompanyResponse]:
        companies = await service.list_companies(limit=limit, offset=offset)
        return CompanyResponse.from_orm_model_list(companies)

    @strawberry.field
    @inject
    async def companies_by_job_id(
        self,
        job_id: UUID,
        service: Injected[CompaniesService],
    ) -> list[CompanyResponse]:
        return CompanyResponse.from_orm_model_list(
            await service.find_companies_by_job_id(job_id)
        )
