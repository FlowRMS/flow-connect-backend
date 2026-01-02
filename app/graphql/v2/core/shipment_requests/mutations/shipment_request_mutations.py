from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.warehouse.shipment_requests import (
    ShipmentMethod,
    ShipmentPriority,
    ShipmentRequest,
    ShipmentRequestStatus,
)

from app.graphql.inject import inject
from app.graphql.v2.core.shipment_requests.services.shipment_request_service import (
    ShipmentRequestService,
)
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_response import (
    ShipmentRequestResponse,
)
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_input import (
    CreateShipmentRequestInput,
)


@strawberry.type
class ShipmentRequestMutations:
    @strawberry.mutation
    @inject
    async def update_shipment_request_status(
        self,
        service: Injected[ShipmentRequestService],
        id: UUID,
        status: ShipmentRequestStatus,
        notes: str | None = None,
    ) -> ShipmentRequestResponse:
        updated_request = await service.update_status(
            request_id=id,
            status=status,
            notes=notes,
        )
        return ShipmentRequestResponse.from_orm_model(updated_request)

    @strawberry.mutation
    @inject
    async def create_shipment_request(
        self,
        service: Injected[ShipmentRequestService],
        input: CreateShipmentRequestInput,
    ) -> ShipmentRequestResponse:
        request = await service.create(
            warehouse_id=input.warehouse_id,
            factory_id=input.factory_id,
            request_date=input.request_date,
            priority=input.priority,
            method=input.method,
            status=input.status,
            notes=input.notes,
            items=input.items,
        )
        return ShipmentRequestResponse.from_orm_model(request)
