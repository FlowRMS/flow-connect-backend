from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.orders.services.order_acknowledgement_service import (
    OrderAcknowledgementService,
)
from app.graphql.orders.strawberry.order_acknowledgement_response import (
    OrderAcknowledgementResponse,
)


@strawberry.type
class OrderAcknowledgementsQueries:
    @strawberry.field
    @inject
    async def order_acknowledgement(
        self,
        id: UUID,
        service: Injected[OrderAcknowledgementService],
    ) -> OrderAcknowledgementResponse | None:
        acknowledgement = await service.get_by_id(id)
        return OrderAcknowledgementResponse.from_orm_model_optional(acknowledgement)

    @strawberry.field
    @inject
    async def order_acknowledgements_by_order(
        self,
        order_id: UUID,
        service: Injected[OrderAcknowledgementService],
    ) -> list[OrderAcknowledgementResponse]:
        acknowledgements = await service.find_by_order_id(order_id)
        return OrderAcknowledgementResponse.from_orm_model_list(acknowledgements)

    @strawberry.field
    @inject
    async def order_acknowledgements_by_order_detail(
        self,
        order_detail_id: UUID,
        service: Injected[OrderAcknowledgementService],
    ) -> list[OrderAcknowledgementResponse]:
        acknowledgements = await service.find_by_order_detail_id(order_detail_id)
        return OrderAcknowledgementResponse.from_orm_model_list(acknowledgements)
