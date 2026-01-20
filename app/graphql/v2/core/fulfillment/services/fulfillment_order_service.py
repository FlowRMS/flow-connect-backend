from datetime import UTC, datetime
from uuid import UUID

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
from app.graphql.addresses.services.address_service import AddressService
from app.graphql.addresses.strawberry.address_input import AddressInput
from app.graphql.v2.core.fulfillment.repositories import (
    FulfillmentActivityRepository,
    FulfillmentAssignmentRepository,
    FulfillmentOrderRepository,
)
from app.graphql.v2.core.fulfillment.strawberry import (
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
        address_service: AddressService,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.activity_repository = activity_repository
        self.assignment_repository = assignment_repository
        self.address_service = address_service
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

        # Handle ship_to_name and ship_to_phone if provided
        if input.ship_to_name:
            order.ship_to_name = input.ship_to_name
        if input.ship_to_phone:
            order.ship_to_phone = input.ship_to_phone

        order = await self.repository.create(order)

        if input.ship_to_address:
            address = await self.address_service.create(input.ship_to_address)
            order.ship_to_address_id = address.id
            order = await self.repository.update(order)

        _ = await self._log_activity(
            order.id, FulfillmentActivityType.CREATED, "Fulfillment order created"
        )
        return order

    async def update(
        self, order_id: UUID, input: UpdateFulfillmentOrderInput
    ) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)

        order.warehouse_id = input.optional_field(
            input.warehouse_id,
            order.warehouse_id,  # pyright: ignore[reportAttributeAccessIssue]
        )
        order.fulfillment_method = input.optional_field(
            input.fulfillment_method,
            order.fulfillment_method,  # pyright: ignore[reportAttributeAccessIssue]
        )
        order.carrier_id = input.optional_field(input.carrier_id, order.carrier_id)
        order.carrier_type = input.optional_field(
            input.carrier_type, order.carrier_type
        )
        order.freight_class = input.optional_field(
            input.freight_class, order.freight_class
        )
        order.service_type = input.optional_field(
            input.service_type, order.service_type
        )
        order.need_by_date = input.optional_field(
            input.need_by_date, order.need_by_date
        )
        order.hold_reason = input.optional_field(input.hold_reason, order.hold_reason)
        order.ship_to_name = input.optional_field(
            input.ship_to_name, order.ship_to_name
        )
        order.ship_to_phone = input.optional_field(
            input.ship_to_phone, order.ship_to_phone
        )

        await self._update_ship_to_address(order, input.ship_to_address)

        return await self.repository.update(order)

    async def _update_ship_to_address(
        self, order: FulfillmentOrder, address_input: AddressInput | None
    ) -> None:
        if address_input is None:
            order.ship_to_address_id = None
            return

        if order.ship_to_address_id:
            _ = await self.address_service.update(
                order.ship_to_address_id, address_input
            )
        else:
            address = await self.address_service.create(address_input)
            order.ship_to_address_id = address.id

    async def release_to_warehouse(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.PENDING:
            raise ValueError("Order must be in PENDING status to release")

        order.status = FulfillmentOrderStatus.RELEASED
        order.released_at = datetime.now(UTC).replace(tzinfo=None)

        # Auto-assign current user as manager
        assignment = FulfillmentAssignment()
        assignment.fulfillment_order_id = order.id
        assignment.user_id = self.auth_info.flow_user_id
        assignment.role = FulfillmentAssignmentRole.MANAGER
        assignment.created_by_id = self.auth_info.flow_user_id
        order.assignments.append(assignment)

        order = await self.repository.update(order)
        _ = await self._log_activity(
            order.id, FulfillmentActivityType.RELEASED, "Order released to warehouse"
        )
        return order

    async def cancel(self, order_id: UUID, reason: str) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)
        order.status = FulfillmentOrderStatus.CANCELLED
        order.hold_reason = reason

        order = await self.repository.update(order)
        _ = await self._log_activity(
            order.id, FulfillmentActivityType.CANCELLED, f"Order cancelled: {reason}"
        )
        return order

    async def bulk_assign(self, input: BulkAssignmentInput) -> list[FulfillmentOrder]:
        orders = []
        for order_id in input.fulfillment_order_ids:
            order = await self._get_or_raise(order_id)

            if input.manager_ids:
                for uid in input.manager_ids:
                    existing = await self.assignment_repository.get_by_order_and_user(
                        order.id, uid
                    )
                    if not existing:
                        assignment = FulfillmentAssignment()
                        assignment.user_id = uid
                        assignment.role = FulfillmentAssignmentRole.MANAGER
                        order.assignments.append(assignment)

            if input.worker_ids:
                for uid in input.worker_ids:
                    existing = await self.assignment_repository.get_by_order_and_user(
                        order.id, uid
                    )
                    if not existing:
                        assignment = FulfillmentAssignment()
                        assignment.user_id = uid
                        assignment.role = FulfillmentAssignmentRole.WORKER
                        order.assignments.append(assignment)

            order = await self.repository.update(order)
            orders.append(order)

        return orders

    async def add_note(self, order_id: UUID, content: str) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)
        _ = await self._log_activity(
            order.id, FulfillmentActivityType.NOTE_ADDED, content
        )
        result = await self.repository.get_with_relations(order.id)
        if not result:
            raise NotFoundError(f"Fulfillment order {order_id} not found")
        return result

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
            activity_metadata=metadata,
        )
        activity.fulfillment_order_id = order_id
        activity.created_by_id = self.auth_info.flow_user_id
        return await self.activity_repository.create(activity)
