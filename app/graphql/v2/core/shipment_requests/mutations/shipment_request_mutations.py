from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.shipment_requests.services.shipment_request_service import (
    ShipmentRequestService,
)
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_response import (
    ShipmentRequestResponse,
    ShipmentRequestStatusEnum,
)


@strawberry.type
class ShipmentRequestMutations:
    @strawberry.mutation
    @inject
    async def update_shipment_request_status(
        self,
        service: Injected[ShipmentRequestService],
        id: UUID,
        status: ShipmentRequestStatusEnum,
        notes: str | None = None,
    ) -> ShipmentRequestResponse:
        updated_request = await service.update_status(
            request_id=id,
            status=status.value,
            notes=notes,
        )
        return ShipmentRequestResponse.from_orm_model(updated_request)
