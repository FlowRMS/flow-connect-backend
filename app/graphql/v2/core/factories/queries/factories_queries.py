from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_response import FactoryResponse


@strawberry.type
class FactoriesQueries:
    """GraphQL queries for Factories entity."""

    @strawberry.field
    @inject
    async def find_factory_by_id(
        self,
        id: UUID,
        service: Injected[FactoryService],
    ) -> FactoryResponse:
        factory = await service.get_by_id(id)
        return FactoryResponse.from_orm_model(factory)

    @strawberry.field
    @inject
    async def factory_search(
        self,
        service: Injected[FactoryService],
        search_term: str,
        published: bool = True,
        limit: int = 20,
        use_custom_order: bool = False,
    ) -> list[FactoryResponse]:
        """
        Search factories by title.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)
            use_custom_order: If True, apply saved custom sort order (default: False)

        Returns:
            List of FactoryResponse objects matching the search criteria
        """
        if use_custom_order:
            factories = await service.search_factories_ordered(
                search_term, published, limit
            )
        else:
            factories = await service.search_factories(search_term, published, limit)
        return FactoryResponse.from_orm_model_list(factories)
