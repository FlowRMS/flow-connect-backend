from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.companies.services.company_types_service import CompanyTypesService
from app.graphql.companies.strawberry.company_type_input import (
    CompanyTypeInput,
)
from app.graphql.companies.strawberry.company_type_response import CompanyTypeResponse
from app.graphql.inject import inject


@strawberry.type
class CompanyTypesMutations:
    @strawberry.mutation
    @inject
    async def create_company_type(
        self,
        input: CompanyTypeInput,
        service: Injected[CompanyTypesService],
    ) -> CompanyTypeResponse:
        company_type = await service.create_type(input)
        return CompanyTypeResponse.from_orm_model(company_type)

    @strawberry.mutation
    @inject
    async def update_company_type(
        self,
        id: UUID,
        input: CompanyTypeInput,
        service: Injected[CompanyTypesService],
    ) -> CompanyTypeResponse:
        company_type = await service.update_type(id, input)
        return CompanyTypeResponse.from_orm_model(company_type)

    @strawberry.mutation
    @inject
    async def delete_company_type(
        self,
        id: UUID,
        service: Injected[CompanyTypesService],
    ) -> bool:
        return await service.delete_type(id)
