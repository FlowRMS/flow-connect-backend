from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_input import CompanyInput
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.inject import inject


@strawberry.type
class CompaniesMutations:
    """GraphQL mutations for Companies entity."""

    @strawberry.mutation
    @inject
    async def create_company(
        self,
        input: CompanyInput,
        service: Injected[CompaniesService],
    ) -> CompanyResponse:
        return CompanyResponse.from_orm_model(
            await service.create_company(company_input=input)
        )

    @strawberry.mutation
    @inject
    async def delete_company(
        self,
        id: UUID,
        service: Injected[CompaniesService],
    ) -> bool:
        return await service.delete_company(company_id=id)

    @strawberry.mutation
    @inject
    async def update_company(
        self,
        id: UUID,
        input: CompanyInput,
        service: Injected[CompaniesService],
    ) -> CompanyResponse:
        """
        Update an existing company.

        Args:
            id: The company ID to update
            input: The updated company data
            service: Injected CompaniesService

        Returns:
            The updated CompanyResponse object
        """
        return CompanyResponse.from_orm_model(await service.update_company(id, input))
