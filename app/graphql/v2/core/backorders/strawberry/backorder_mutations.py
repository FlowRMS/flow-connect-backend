from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.backorders.services.backorder_service import BackorderService
from app.graphql.v2.core.backorders.strawberry.backorder_input import BackorderItemInput
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_response import (
    ShipmentRequestResponse,
)


@strawberry.type
class BackorderMutations:
    @strawberry.mutation
    @inject
    async def resolve_backorder_restock(
        self,
        service: Injected[BackorderService],
        factory_id: UUID,
        items: list[BackorderItemInput],
        warehouse_id: UUID,
    ) -> ShipmentRequestResponse:
        """
        Create a restock shipment request (Factory -> Warehouse).
        """
        request = await service.restock(
            factory_id=factory_id,
            items=[(i.product_id, i.quantity) for i in items],
            warehouse_id=warehouse_id,
        )
        return ShipmentRequestResponse.from_orm_model(request)

    @strawberry.mutation
    @inject
    async def resolve_backorder_dropship(
        self,
        service: Injected[BackorderService],
        factory_id: UUID,
        items: list[BackorderItemInput],
        customer_id: UUID,
    ) -> ShipmentRequestResponse:
        """
        Create a dropship shipment request (Factory -> Customer).
        """
        request = await service.dropship(
            factory_id=factory_id,
            items=[(i.product_id, i.quantity) for i in items],
            customer_id=customer_id,
        )
        return ShipmentRequestResponse.from_orm_model(request)
