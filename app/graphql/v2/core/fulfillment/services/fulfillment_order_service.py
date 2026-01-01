from datetime import datetime, timezone
from uuid import UUID

import strawberry
from commons.auth import AuthInfo
from commons.db.v6.fulfillment import (
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentAssignment,
    FulfillmentAssignmentRole,
    FulfillmentOrder,
    FulfillmentOrderStatus,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.fulfillment.repositories import (
    FulfillmentActivityRepository,
    FulfillmentAssignmentRepository,
    FulfillmentOrderRepository,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_input import (
    BulkAssignmentInput,
    CreateFulfillmentOrderInput,
    UpdateFulfillmentOrderInput,
)


class FulfillmentOrderService:
    def __init__(
        self,
        repository: FulfillmentOrderRepository,
        activity_repository: FulfillmentActivityRepository,
        assignment_repository: FulfillmentAssignmentRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.activity_repository = activity_repository
        self.assignment_repository = assignment_repository
        self.auth_info = auth_info

    async def get_by_id(self, order_id: UUID) -> FulfillmentOrder | None:
        return await self.repository.get_with_relations(order_id)

    async def list_orders(
        self,
        warehouse_id: UUID | None = None,
        status: list[FulfillmentOrderStatus] | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FulfillmentOrder]:
        return await self.repository.list_orders(
            warehouse_id=warehouse_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def get_stats(self, warehouse_id: UUID | None = None) -> dict[str, int]:
        return await self.repository.get_stats(warehouse_id)

    async def create(self, input: CreateFulfillmentOrderInput) -> FulfillmentOrder:
        order = input.to_orm_model()
        next_number = await self.repository.get_next_order_number()
        order.fulfillment_order_number = f"FO-{next_number:06d}"

        order = await self.repository.create(order)
        await self._log_activity(
            order.id, FulfillmentActivityType.CREATED, "Fulfillment order created"
        )
        return order

    async def update(
        self, order_id: UUID, input: UpdateFulfillmentOrderInput
    ) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)

        if input.warehouse_id is not strawberry.UNSET:
            order.warehouse_id = input.warehouse_id
        if input.carrier_id is not strawberry.UNSET:
            order.carrier_id = input.carrier_id
        if input.carrier_type is not strawberry.UNSET:
            order.carrier_type = input.carrier_type
        if input.need_by_date is not strawberry.UNSET:
            order.need_by_date = input.need_by_date
        if input.hold_reason is not strawberry.UNSET:
            order.hold_reason = input.hold_reason

        return await self.repository.update(order)

    async def release_to_warehouse(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.PENDING:
            raise ValueError("Order must be in PENDING status to release")

        order.status = FulfillmentOrderStatus.RELEASED
        order.released_at = datetime.now(timezone.utc)

        # Auto-assign current user as manager
        assignment = FulfillmentAssignment(
            user_id=self.auth_info.flow_user_id,
            role=FulfillmentAssignmentRole.MANAGER,
        )
        order.assignments.append(assignment)

        order = await self.repository.update(order)
        await self._log_activity(
            order.id, FulfillmentActivityType.RELEASED, "Order released to warehouse"
        )
        return order

    async def cancel(self, order_id: UUID, reason: str) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)
        order.status = FulfillmentOrderStatus.CANCELLED
        order.hold_reason = reason

        order = await self.repository.update(order)
        await self._log_activity(
            order.id, FulfillmentActivityType.CANCELLED, f"Order cancelled: {reason}"
        )
        return order

    async def bulk_assign(self, input: BulkAssignmentInput) -> list[FulfillmentOrder]:
        orders = []
        for order_id in input.fulfillment_order_ids:
            order = await self._get_or_raise(order_id)

            if input.manager_ids:
                for user_id in input.manager_ids:
                    existing = await self.assignment_repository.get_by_order_and_user(
                        order.id, user_id
                    )
                    if not existing:
                        assignment = FulfillmentAssignment(
                            user_id=user_id,
                            role=FulfillmentAssignmentRole.MANAGER,
                        )
                        order.assignments.append(assignment)

            if input.worker_ids:
                for user_id in input.worker_ids:
                    existing = await self.assignment_repository.get_by_order_and_user(
                        order.id, user_id
                    )
                    if not existing:
                        assignment = FulfillmentAssignment(
                            user_id=user_id,
                            role=FulfillmentAssignmentRole.WORKER,
                        )
                        order.assignments.append(assignment)

            order = await self.repository.update(order)
            orders.append(order)

        return orders

    async def add_note(self, order_id: UUID, content: str) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)
        await self._log_activity(order.id, FulfillmentActivityType.NOTE_ADDED, content)
        return await self.repository.get_with_relations(order.id)

    async def _get_or_raise(self, order_id: UUID) -> FulfillmentOrder:
        order = await self.repository.get_with_relations(order_id)
        if not order:
            raise NotFoundError(f"Fulfillment order {order_id} not found")
        return order

    async def _log_activity(
        self,
        order_id: UUID,
        activity_type: FulfillmentActivityType,
        content: str,
        metadata: dict | None = None,
    ) -> FulfillmentActivity:
        activity = FulfillmentActivity(
            activity_type=activity_type,
            content=content,
            metadata=metadata,
        )
        activity.fulfillment_order_id = order_id
        activity.created_by_id = self.auth_info.flow_user_id
        return await self.activity_repository.create(activity)
