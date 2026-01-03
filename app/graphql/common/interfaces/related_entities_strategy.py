from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from app.graphql.common.landing_source_type import LandingSourceType

if TYPE_CHECKING:
    from app.graphql.common.strawberry.related_entities_response import (
        RelatedEntitiesResponse,
    )


class RelatedEntitiesStrategy(ABC):
    @abstractmethod
    def get_supported_source_type(self) -> LandingSourceType:
        pass

    @abstractmethod
    async def get_related_entities(
        self,
        entity_id: UUID,
    ) -> "RelatedEntitiesResponse":
        pass


class RelatedEntitiesStrategyRegistry:
    def __init__(self) -> None:
        super().__init__()
        self._strategies: dict[LandingSourceType, RelatedEntitiesStrategy] = {}

    def register(self, strategy: RelatedEntitiesStrategy) -> None:
        source_type = strategy.get_supported_source_type()
        self._strategies[source_type] = strategy

    def get_by_source_type(
        self, source_type: LandingSourceType
    ) -> RelatedEntitiesStrategy | None:
        return self._strategies.get(source_type)
