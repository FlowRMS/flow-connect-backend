from decimal import Decimal
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.fulfillment.services import (
    FulfillmentPackingService,
    FulfillmentPickingService,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    AssignItemToBoxInput,
    CreatePackingBoxInput,
    FulfillmentOrderLineItemResponse,
    FulfillmentOrderResponse,
    PackingBoxResponse,
    UpdatePackingBoxInput,
    UpdatePickedQuantityInput,
)


@strawberry.type
class FulfillmentPickingMutations:
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
