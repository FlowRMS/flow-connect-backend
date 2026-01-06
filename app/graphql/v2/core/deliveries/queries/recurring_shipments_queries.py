
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.recurring_shipment_service import (
    RecurringShipmentService,
)
from app.graphql.v2.core.deliveries.strawberry.recurring_shipment_response import (
    RecurringShipmentResponse,
)


@strawberry.type
class RecurringShipmentsQueries:
    """GraphQL queries for RecurringShipment entity."""

    @strawberry.field
    @inject
    async def recurring_shipments(
        self,
        service: Injected[RecurringShipmentService],
        warehouse_id: UUID | None = None,
    ) -> list[RecurringShipmentResponse]:
        if warehouse_id:
            shipments = await service.list_by_warehouse(warehouse_id)
        else:
            shipments = await service.list_all()
        return RecurringShipmentResponse.from_orm_model_list(shipments)

    @strawberry.field
    @inject
    async def recurring_shipment(
        self,
        id: UUID,
        service: Injected[RecurringShipmentService],
    ) -> RecurringShipmentResponse:
        shipment = await service.get_by_id(id)
        return RecurringShipmentResponse.from_orm_model(shipment)
