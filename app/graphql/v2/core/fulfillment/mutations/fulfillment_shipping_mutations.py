from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.fulfillment.services import (
    FulfillmentBackorderService,
    FulfillmentDocumentService,
    FulfillmentShippingService,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    AddDocumentInput,
    CancelBackorderInput,
    CompleteShippingInput,
    FulfillmentDocumentResponse,
    FulfillmentOrderLineItemResponse,
    FulfillmentOrderResponse,
    LinkShipmentRequestInput,
    MarkManufacturerFulfilledInput,
    SplitLineItemInput,
    UploadDocumentInput,
)


@strawberry.type
class FulfillmentShippingMutations:
    # ─────────────────────────────────────────────────────────────────
    # Shipping
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def complete_shipping(
        self,
        id: UUID,
        input: CompleteShippingInput,
        service: Injected[FulfillmentShippingService],
    ) -> FulfillmentOrderResponse:
        order = await service.complete_shipping(id, input)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def mark_communicated(
        self,
        id: UUID,
        service: Injected[FulfillmentShippingService],
    ) -> FulfillmentOrderResponse:
        order = await service.mark_communicated(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def mark_delivered(
        self,
        id: UUID,
        service: Injected[FulfillmentShippingService],
    ) -> FulfillmentOrderResponse:
        order = await service.mark_delivered(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Backorder Handling
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def mark_manufacturer_fulfilled(
        self,
        input: MarkManufacturerFulfilledInput,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderResponse:
        order = await service.mark_manufacturer_fulfilled(
            input.fulfillment_order_id,
            input.line_item_ids,
        )
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def split_fulfillment_line_item(
        self,
        input: SplitLineItemInput,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderLineItemResponse:
        line_item = await service.split_line_item(
            input.line_item_id,
            input.warehouse_qty,
            input.manufacturer_qty,
        )
        return FulfillmentOrderLineItemResponse.from_orm_model(line_item)

    @strawberry.mutation
    @inject
    async def cancel_backorder_items(
        self,
        input: CancelBackorderInput,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderResponse:
        order = await service.cancel_backorder_items(
            input.fulfillment_order_id,
            input.line_item_ids,
            input.reason,
        )
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def link_shipment_request(
        self,
        input: LinkShipmentRequestInput,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderResponse:
        order = await service.link_shipment_request(
            input.fulfillment_order_id,
            input.line_item_ids,
            input.shipment_request_id,
        )
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def resolve_backorder(
        self,
        fulfillment_order_id: UUID,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderResponse:
        order = await service.resolve_backorder(fulfillment_order_id)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Documents
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def add_document(
        self,
        input: AddDocumentInput,
        service: Injected[FulfillmentDocumentService],
    ) -> FulfillmentDocumentResponse:
        document = await service.add_document(
            input.fulfillment_order_id,
            input.document_type,
            input.file_name,
            input.file_url,
            input.file_size,
            input.mime_type,
            input.notes,
        )
        return FulfillmentDocumentResponse.from_orm_model(document)

    @strawberry.mutation
    @inject
    async def upload_document(
        self,
        input: UploadDocumentInput,
        service: Injected[FulfillmentDocumentService],
    ) -> FulfillmentDocumentResponse:
        document = await service.upload_document(
            input.fulfillment_order_id,
            input.document_type,
            input.file,
            input.notes,
        )
        return FulfillmentDocumentResponse.from_orm_model(document)

    @strawberry.mutation
    @inject
    async def delete_document(
        self,
        document_id: UUID,
        service: Injected[FulfillmentDocumentService],
    ) -> bool:
        return await service.delete_document(document_id)
