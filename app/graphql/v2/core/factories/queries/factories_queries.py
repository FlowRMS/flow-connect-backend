from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
    FactoryResponse,
)


@strawberry.type
class FactoriesQueries:
    """GraphQL queries for Factories entity."""

    @strawberry.field
    @inject
    async def factory(
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

    @strawberry.field
    @inject
    async def factory_children(
        self,
        service: Injected[FactoryService],
        parent_id: UUID,
    ) -> list[FactoryLiteResponse]:
        """
        Get all child factories for a given parent factory.

        Args:
            parent_id: The ID of the parent factory

        Returns:
            List of FactoryLiteResponse objects for children of the parent
        """
        children = await service.get_children(parent_id)
        return FactoryLiteResponse.from_orm_model_list(children)
