
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_item_receipt_service import (
    DeliveryItemReceiptService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_item_receipt_response import (
    DeliveryItemReceiptResponse,
)


@strawberry.type
class DeliveryItemReceiptsQueries:
    """GraphQL queries for DeliveryItemReceipt entity."""

    @strawberry.field
    @inject
    async def delivery_item_receipts(
        self,
        delivery_item_id: UUID,
        service: Injected[DeliveryItemReceiptService],
    ) -> list[DeliveryItemReceiptResponse]:
        receipts = await service.list_by_delivery_item(delivery_item_id)
        return DeliveryItemReceiptResponse.from_orm_model_list(receipts)

    @strawberry.field
    @inject
    async def delivery_item_receipt(
        self,
        id: UUID,
        service: Injected[DeliveryItemReceiptService],
    ) -> DeliveryItemReceiptResponse:
        receipt = await service.get_by_id(id)
        return DeliveryItemReceiptResponse.from_orm_model(receipt)
