from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.orders.services.order_acknowledgement_service import (
    OrderAcknowledgementService,
)
from app.graphql.orders.strawberry.order_acknowledgement_input import (
    OrderAcknowledgementInput,
)
from app.graphql.orders.strawberry.order_acknowledgement_response import (
    OrderAcknowledgementResponse,
)


@strawberry.type
class OrderAcknowledgementsMutations:
    @strawberry.mutation
    @inject
    async def create_order_acknowledgement(
        self,
        input: OrderAcknowledgementInput,
        service: Injected[OrderAcknowledgementService],
    ) -> OrderAcknowledgementResponse:
        acknowledgement = await service.create(input)
        return OrderAcknowledgementResponse.from_orm_model(acknowledgement)

    @strawberry.mutation
    @inject
    async def update_order_acknowledgement(
        self,
        input: OrderAcknowledgementInput,
        service: Injected[OrderAcknowledgementService],
    ) -> OrderAcknowledgementResponse:
        acknowledgement = await service.update(input)
        return OrderAcknowledgementResponse.from_orm_model(acknowledgement)

    @strawberry.mutation
    @inject
    async def delete_order_acknowledgement(
        self,
        id: UUID,
        service: Injected[OrderAcknowledgementService],
    ) -> bool:
        return await service.delete(id)
