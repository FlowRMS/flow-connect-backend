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
