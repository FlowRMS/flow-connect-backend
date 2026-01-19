from uuid import UUID

from app.errors.common_errors import NotFoundError
from app.graphql.common.interfaces.related_entities_strategy import (
    RelatedEntitiesStrategyRegistry,
)
from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.common.strawberry.related_entities_response import (
    RelatedEntitiesResponse,
)


class RelatedEntitiesService:
    def __init__(
        self,
        strategy_registry: RelatedEntitiesStrategyRegistry,
    ) -> None:
        super().__init__()
        self.strategy_registry = strategy_registry

    async def get_related_entities(
        self,
        source_type: LandingSourceType,
        entity_id: UUID,
    ) -> RelatedEntitiesResponse:
        strategy = self.strategy_registry.get_by_source_type(source_type)
        if not strategy:
            raise NotFoundError(
                f"No related entities strategy for source type: {source_type.value}"
            )
        return await strategy.get_related_entities(entity_id)
