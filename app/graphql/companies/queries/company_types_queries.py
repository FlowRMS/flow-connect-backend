from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.companies.services.company_types_service import CompanyTypesService
from app.graphql.companies.strawberry.company_type_response import CompanyTypeResponse
from app.graphql.inject import inject


@strawberry.type
class CompanyTypesQueries:

    @strawberry.field
    @inject
    async def company_types(
        self,
        service: Injected[CompanyTypesService],
        include_inactive: bool = False,
    ) -> list[CompanyTypeResponse]:
        types = await service.list_types(include_inactive=include_inactive)
        return CompanyTypeResponse.from_orm_model_list(types)

    @strawberry.field
    @inject
    async def company_type(
        self,
        id: UUID,
        service: Injected[CompanyTypesService],
    ) -> CompanyTypeResponse:
        company_type = await service.get_type_by_id(id)
        return CompanyTypeResponse.from_orm_model(company_type)
