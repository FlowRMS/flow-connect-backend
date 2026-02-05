from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.fulfillment.enums import FulfillmentAssignmentRole

from app.graphql.inject import inject
from app.graphql.v2.core.fulfillment.services import (
    FulfillmentAssignmentService,
    FulfillmentOrderService,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    BulkAssignmentInput,
    CreateFulfillmentOrderInput,
    FulfillmentOrderResponse,
    UpdateFulfillmentOrderInput,
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
        order = await service.add_assignment(fulfillment_order_id, user_id, role)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def remove_fulfillment_assignment(
        self,
        assignment_id: UUID,
        service: Injected[FulfillmentAssignmentService],
    ) -> FulfillmentOrderResponse:
        order = await service.remove_assignment(assignment_id)
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
