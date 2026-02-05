from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.inject import inject


@strawberry.type
class CompaniesQueries:
    """GraphQL queries for Companies entity."""

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
    async def company_search(
        self,
        service: Injected[CompaniesService],
        search_term: str,
        limit: int = 20,
    ) -> list[CompanyResponse]:
        """
        Search companies by name.

        Args:
            search_term: The search term to match against company name
            limit: Maximum number of companies to return (default: 20)

        Returns:
            List of CompanyResponse objects matching the search criteria
        """
        return CompanyResponse.from_orm_model_list(
            await service.search_companies(search_term, limit)
        )
