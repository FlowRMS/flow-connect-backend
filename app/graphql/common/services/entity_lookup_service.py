from uuid import UUID

from app.errors.common_errors import NotFoundError
from app.graphql.common.entity_source_type import EntitySourceType
from app.graphql.common.interfaces.entity_lookup_strategy import (
    EntityLookupStrategyRegistry,
)
from app.graphql.common.strawberry.entity_response import EntityResponse


class EntityLookupService:
    def __init__(
        self,
        strategy_registry: EntityLookupStrategyRegistry,
    ) -> None:
        super().__init__()
        self.strategy_registry = strategy_registry

    async def get_entity(
        self,
        source_type: EntitySourceType,
        entity_id: UUID,
    ) -> EntityResponse:
        strategy = self.strategy_registry.get_by_source_type(source_type)
        if not strategy:
            raise NotFoundError(
                f"No entity lookup strategy for source type: {source_type.value}"
            )
        return await strategy.get_entity(entity_id)
