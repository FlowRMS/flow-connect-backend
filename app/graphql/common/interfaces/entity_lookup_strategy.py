from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from app.graphql.common.entity_source_type import EntitySourceType

if TYPE_CHECKING:
    from app.graphql.common.strawberry.entity_response import EntityResponse


class EntityLookupStrategy(ABC):
    @abstractmethod
    def get_supported_source_type(self) -> EntitySourceType:
        pass

    @abstractmethod
    async def get_entity(self, entity_id: UUID) -> "EntityResponse":
        pass


class EntityLookupStrategyRegistry:
    def __init__(self) -> None:
        super().__init__()
        self._strategies: dict[EntitySourceType, EntityLookupStrategy] = {}

    def register(self, strategy: EntityLookupStrategy) -> None:
        source_type = strategy.get_supported_source_type()
        self._strategies[source_type] = strategy

    def get_by_source_type(
        self, source_type: EntitySourceType
    ) -> EntityLookupStrategy | None:
        return self._strategies.get(source_type)
