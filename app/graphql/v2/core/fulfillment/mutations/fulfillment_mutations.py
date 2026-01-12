from decimal import Decimal
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.fulfillment import FulfillmentAssignmentRole

from app.graphql.inject import inject
from app.graphql.v2.core.fulfillment.services import (
    FulfillmentAssignmentService,
    FulfillmentBackorderService,
    FulfillmentDocumentService,
    FulfillmentOrderService,
    FulfillmentPackingService,
    FulfillmentPickingService,
    FulfillmentShippingService,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    AddDocumentInput,
    AssignItemToBoxInput,
    BulkAssignmentInput,
    CancelBackorderInput,
    CompleteShippingInput,
    CreateFulfillmentOrderInput,
    CreatePackingBoxInput,
    FulfillmentDocumentResponse,
    FulfillmentOrderLineItemResponse,
    FulfillmentOrderResponse,
    MarkManufacturerFulfilledInput,
    PackingBoxResponse,
    SplitLineItemInput,
    UpdateFulfillmentOrderInput,
    UpdatePackingBoxInput,
    UpdatePickedQuantityInput,
    UploadDocumentInput,
)


@strawberry.type
class FulfillmentMutations:
    # ─────────────────────────────────────────────────────────────────
    # Order Lifecycle
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def create_fulfillment_order(
        self,
        input: CreateFulfillmentOrderInput,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.create(input)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def update_fulfillment_order(
        self,
        id: UUID,
        input: UpdateFulfillmentOrderInput,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.update(id, input)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def release_to_warehouse(
        self,
        id: UUID,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.release_to_warehouse(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def cancel_fulfillment_order(
        self,
        id: UUID,
        reason: str,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.cancel(id, reason)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Assignments
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def bulk_assign_fulfillment_orders(
        self,
        input: BulkAssignmentInput,
        service: Injected[FulfillmentOrderService],
    ) -> list[FulfillmentOrderResponse]:
        orders = await service.bulk_assign(input)
        return FulfillmentOrderResponse.from_orm_model_list(orders)

    @strawberry.mutation
    @inject
    async def add_fulfillment_assignment(
        self,
        fulfillment_order_id: UUID,
        user_id: UUID,
        role: FulfillmentAssignmentRole,
        service: Injected[FulfillmentAssignmentService],
    ) -> FulfillmentOrderResponse:
        """Add a user assignment to a fulfillment order."""
        order = await service.add_assignment(fulfillment_order_id, user_id, role)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def remove_fulfillment_assignment(
        self,
        assignment_id: UUID,
        service: Injected[FulfillmentAssignmentService],
    ) -> FulfillmentOrderResponse:
        """Remove an assignment from a fulfillment order."""
        order = await service.remove_assignment(assignment_id)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Picking
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def start_picking(
        self,
        id: UUID,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderResponse:
        order = await service.start_picking(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def update_picked_quantity(
        self,
        input: UpdatePickedQuantityInput,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderLineItemResponse:
        line_item = await service.update_picked_quantity(
            line_item_id=input.line_item_id,
            quantity=input.quantity,
            notes=input.notes,
        )
        return FulfillmentOrderLineItemResponse.from_orm_model(line_item)

    @strawberry.mutation
    @inject
    async def complete_picking(
        self,
        id: UUID,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderResponse:
        order = await service.complete_picking(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def report_inventory_discrepancy(
        self,
        line_item_id: UUID,
        actual_quantity: Decimal,
        reason: str,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderResponse:
        order = await service.report_discrepancy(line_item_id, actual_quantity, reason)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Packing
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def add_packing_box(
        self,
        fulfillment_order_id: UUID,
        input: CreatePackingBoxInput,
        service: Injected[FulfillmentPackingService],
    ) -> PackingBoxResponse:
        box = await service.add_box(fulfillment_order_id, input)
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def update_packing_box(
        self,
        box_id: UUID,
        input: UpdatePackingBoxInput,
        service: Injected[FulfillmentPackingService],
    ) -> PackingBoxResponse:
        box = await service.update_box(box_id, input)
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def assign_item_to_box(
        self,
        input: AssignItemToBoxInput,
        service: Injected[FulfillmentPackingService],
    ) -> PackingBoxResponse:
        box = await service.assign_item_to_box(
            box_id=input.box_id,
            line_item_id=input.line_item_id,
            quantity=input.quantity,
        )
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def remove_item_from_box(
        self,
        box_id: UUID,
        line_item_id: UUID,
        service: Injected[FulfillmentPackingService],
    ) -> PackingBoxResponse:
        box = await service.remove_item_from_box(box_id, line_item_id)
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def delete_packing_box(
        self,
        box_id: UUID,
        service: Injected[FulfillmentPackingService],
    ) -> bool:
        return await service.delete_box(box_id)

    @strawberry.mutation
    @inject
    async def complete_packing(
        self,
        id: UUID,
        service: Injected[FulfillmentPackingService],
    ) -> FulfillmentOrderResponse:
        order = await service.complete_packing(id)
        return FulfillmentOrderResponse.from_orm_model(order)

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
    # Notes
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def add_fulfillment_note(
        self,
        fulfillment_order_id: UUID,
        content: str,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.add_note(fulfillment_order_id, content)
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
        """Mark line items as being fulfilled directly by manufacturer."""
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
        """Split a line item between warehouse and manufacturer fulfillment."""
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
        """Cancel backorder items and adjust quantities."""
        order = await service.cancel_backorder_items(
            input.fulfillment_order_id,
            input.line_item_ids,
            input.reason,
        )
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def resolve_backorder(
        self,
        fulfillment_order_id: UUID,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderResponse:
        """Resolve backorder status and continue fulfillment."""
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
        """Add a document to a fulfillment order."""
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
        """Upload a file and attach to fulfillment order."""
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
        """Delete a document from a fulfillment order."""
        return await service.delete_document(document_id)
