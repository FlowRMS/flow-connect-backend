
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_item_receipt_service import (
    DeliveryItemReceiptService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import (
    DeliveryItemReceiptInput,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_item_receipt_response import (
    DeliveryItemReceiptResponse,
)


@strawberry.type
class DeliveryItemReceiptsMutations:
    """GraphQL mutations for DeliveryItemReceipt entity."""

    @strawberry.mutation
    @inject
    async def create_delivery_item_receipt(
        self,
        input: DeliveryItemReceiptInput,
        service: Injected[DeliveryItemReceiptService],
    ) -> DeliveryItemReceiptResponse:
        receipt = await service.create(input)
        return DeliveryItemReceiptResponse.from_orm_model(receipt)

    @strawberry.mutation
    @inject
    async def update_delivery_item_receipt(
        self,
        id: UUID,
        input: DeliveryItemReceiptInput,
        service: Injected[DeliveryItemReceiptService],
    ) -> DeliveryItemReceiptResponse:
        receipt = await service.update(id, input)
        return DeliveryItemReceiptResponse.from_orm_model(receipt)

    @strawberry.mutation
    @inject
    async def delete_delivery_item_receipt(
        self,
        id: UUID,
        service: Injected[DeliveryItemReceiptService],
    ) -> bool:
        return await service.delete(id)
