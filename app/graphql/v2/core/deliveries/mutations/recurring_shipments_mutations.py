
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.recurring_shipment_service import (
    RecurringShipmentService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import (
    RecurringShipmentInput,
)
from app.graphql.v2.core.deliveries.strawberry.recurring_shipment_response import (
    RecurringShipmentResponse,
)


@strawberry.type
class RecurringShipmentsMutations:
    """GraphQL mutations for RecurringShipment entity."""

    @strawberry.mutation
    @inject
    async def create_recurring_shipment(
        self,
        input: RecurringShipmentInput,
        service: Injected[RecurringShipmentService],
    ) -> RecurringShipmentResponse:
        shipment = await service.create(input)
        return RecurringShipmentResponse.from_orm_model(shipment)

    @strawberry.mutation
    @inject
    async def update_recurring_shipment(
        self,
        id: UUID,
        input: RecurringShipmentInput,
        service: Injected[RecurringShipmentService],
    ) -> RecurringShipmentResponse:
        shipment = await service.update(id, input)
        return RecurringShipmentResponse.from_orm_model(shipment)

    @strawberry.mutation
    @inject
    async def delete_recurring_shipment(
        self,
        id: UUID,
        service: Injected[RecurringShipmentService],
    ) -> bool:
        return await service.delete(id)
