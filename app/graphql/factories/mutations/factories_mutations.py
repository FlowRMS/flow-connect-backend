"""GraphQL mutations for Factories entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.factories.services.factory_service import FactoryService
from app.graphql.inject import inject


@strawberry.type
class FactoriesMutations:
    """GraphQL mutations for Factories entity."""

    @strawberry.mutation
    @inject
    async def update_manufacturer_order(
        self,
        service: Injected[FactoryService],
        factory_ids: list[UUID],
    ) -> int:
        """
        Update the display order of manufacturers.

        Args:
            factory_ids: List of factory UUIDs in the desired display order

        Returns:
            Number of manufacturers updated
        """
        return await service.update_manufacturer_order(factory_ids)
