from uuid import UUID

from app.errors.common_errors import NotFoundError
from app.graphql.common.bulk_delete_entity_type import BulkDeleteEntityType
from app.graphql.common.interfaces.bulk_delete_strategy import (
    BulkDeleteStrategyRegistry,
)
from app.graphql.common.strawberry.bulk_delete_response import BulkDeleteResult


class BulkDeleteService:
    def __init__(self, strategy_registry: BulkDeleteStrategyRegistry) -> None:
        super().__init__()
        self.strategy_registry = strategy_registry

    async def delete_entities(
        self,
        entity_type: BulkDeleteEntityType,
        entity_ids: list[UUID],
    ) -> BulkDeleteResult:
        strategy = self.strategy_registry.get_by_entity_type(entity_type)
        if not strategy:
            raise NotFoundError(
                f"No bulk delete strategy for entity type: {entity_type.value}"
            )
        return await strategy.delete_entities(entity_ids)
