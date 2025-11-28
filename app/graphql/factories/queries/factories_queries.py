import strawberry
from aioinject import Injected

from app.graphql.factories.services.factory_service import FactoryService
from app.graphql.factories.strawberry.factory_response import FactoryResponse
from app.graphql.inject import inject


@strawberry.type
class FactoriesQueries:
    """GraphQL queries for Factories entity."""

    @strawberry.field
    @inject
    async def factory_search(
        self,
        service: Injected[FactoryService],
        search_term: str,
        published: bool = True,
        limit: int = 20,
    ) -> list[FactoryResponse]:
        """
        Search factories by title.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)

        Returns:
            List of FactoryResponse objects matching the search criteria
        """
        return FactoryResponse.from_orm_model_list(
            await service.search_factories(search_term, published, limit)
        )
