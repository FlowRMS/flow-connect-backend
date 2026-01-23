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
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryStatusHistoryInput


@strawberry.type
class DeliveryStatusHistoryMutations:
    """GraphQL mutations for DeliveryStatusHistory entity."""

    @strawberry.mutation
    @inject
    async def create_delivery_status_history(
        self,
        input: DeliveryStatusHistoryInput,
        service: Injected[DeliveryStatusHistoryService],
    ) -> DeliveryStatusHistoryResponse:
        entry = await service.create(input)
        return DeliveryStatusHistoryResponse.from_orm_model(entry)

    @strawberry.mutation
    @inject
    async def update_delivery_status_history(
        self,
        id: UUID,
        input: DeliveryStatusHistoryInput,
        service: Injected[DeliveryStatusHistoryService],
    ) -> DeliveryStatusHistoryResponse:
        entry = await service.update(id, input)
        return DeliveryStatusHistoryResponse.from_orm_model(entry)

    @strawberry.mutation
    @inject
    async def delete_delivery_status_history(
        self,
        id: UUID,
        service: Injected[DeliveryStatusHistoryService],
    ) -> bool:
        return await service.delete(id)
