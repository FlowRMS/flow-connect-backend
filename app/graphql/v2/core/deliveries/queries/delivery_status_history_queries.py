from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_status_history_service import (
    DeliveryStatusHistoryService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_status_history_response import (
    DeliveryStatusHistoryResponse,
)


@strawberry.type
class DeliveryStatusHistoryQueries:
    """GraphQL queries for DeliveryStatusHistory entity."""

    @strawberry.field
    @inject
    async def delivery_status_history(
        self,
        delivery_id: UUID,
        service: Injected[DeliveryStatusHistoryService],
    ) -> list[DeliveryStatusHistoryResponse]:
        history = await service.list_by_delivery(delivery_id)
        return DeliveryStatusHistoryResponse.from_orm_model_list(history)

    @strawberry.field
    @inject
    async def delivery_status_entry(
        self,
        id: UUID,
        service: Injected[DeliveryStatusHistoryService],
    ) -> DeliveryStatusHistoryResponse:
        entry = await service.get_by_id(id)
        return DeliveryStatusHistoryResponse.from_orm_model(entry)
