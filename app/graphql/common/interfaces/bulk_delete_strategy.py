from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from app.graphql.common.bulk_delete_entity_type import BulkDeleteEntityType

if TYPE_CHECKING:
    from app.graphql.common.strawberry.bulk_delete_response import BulkDeleteResult


class BulkDeleteStrategy(ABC):
    @abstractmethod
    def get_supported_entity_type(self) -> BulkDeleteEntityType:
        pass

    @abstractmethod
    async def delete_entities(self, entity_ids: list[UUID]) -> "BulkDeleteResult":
        pass


class BulkDeleteStrategyRegistry:
    def __init__(self) -> None:
        super().__init__()
        self._strategies: dict[BulkDeleteEntityType, BulkDeleteStrategy] = {}

    def register(self, strategy: BulkDeleteStrategy) -> None:
        entity_type = strategy.get_supported_entity_type()
        self._strategies[entity_type] = strategy

    def get_by_entity_type(
        self, entity_type: BulkDeleteEntityType
    ) -> BulkDeleteStrategy | None:
        return self._strategies.get(entity_type)
