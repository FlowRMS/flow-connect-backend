from datetime import UTC, datetime
from uuid import UUID

import strawberry
from commons.auth import AuthInfo
from commons.db.v6.core.addresses.address import Address, AddressSourceTypeEnum
from commons.db.v6.fulfillment import (
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentAssignment,
    FulfillmentAssignmentRole,
    FulfillmentOrder,
    FulfillmentOrderStatus,
)

from app.errors.common_errors import NotFoundError
from app.graphql.addresses.repositories.address_repository import AddressRepository
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
        address_repository: AddressRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.activity_repository = activity_repository
        self.assignment_repository = assignment_repository
        self.address_repository = address_repository
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

        # Handle ship_to_address if provided
        if input.ship_to_address:
            order.ship_to_name = input.ship_to_address.name
            order.ship_to_phone = input.ship_to_address.phone

        order = await self.repository.create(order)

        # Create Address record after order is created (need order.id for source_id)
        if input.ship_to_address:
            address_fields = input.ship_to_address.to_address_fields()
            address = Address(
                source_id=order.id,
                source_type=AddressSourceTypeEnum.FULFILLMENT_ORDER,
                is_primary=True,
                **address_fields,
            )
            address = await self.address_repository.create(address)
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

        if (
            input.warehouse_id is not strawberry.UNSET
            and input.warehouse_id is not None
        ):
            order.warehouse_id = input.warehouse_id
        if (
            input.fulfillment_method is not strawberry.UNSET
            and input.fulfillment_method is not None
        ):
            order.fulfillment_method = input.fulfillment_method
        if input.carrier_id is not strawberry.UNSET:
            order.carrier_id = input.carrier_id
        if input.carrier_type is not strawberry.UNSET:
            order.carrier_type = input.carrier_type
        if input.freight_class is not strawberry.UNSET:
            order.freight_class = input.freight_class
        if input.need_by_date is not strawberry.UNSET:
            order.need_by_date = input.need_by_date
        if input.hold_reason is not strawberry.UNSET:
            order.hold_reason = input.hold_reason
        if input.ship_to_address is not strawberry.UNSET:
            if input.ship_to_address is None:
                # Clear the address reference
                order.ship_to_address_id = None
                order.ship_to_name = None
                order.ship_to_phone = None
            else:
                # Update name and phone on the order
                order.ship_to_name = input.ship_to_address.name
                order.ship_to_phone = input.ship_to_address.phone
                address_fields = input.ship_to_address.to_address_fields()

                if order.ship_to_address_id:
                    # Update existing address
                    existing_address = await self.address_repository.get_by_id(
                        order.ship_to_address_id
                    )
                    if existing_address:
                        existing_address.line_1 = address_fields["line_1"]
                        existing_address.line_2 = address_fields["line_2"]
                        existing_address.city = address_fields["city"]
                        existing_address.state = address_fields["state"]
                        existing_address.zip_code = address_fields["zip_code"]
                        existing_address.country = address_fields["country"]
                        await self.address_repository.update(existing_address)
                else:
                    # Create new address
                    address = Address(
                        source_id=order.id,
                        source_type=AddressSourceTypeEnum.FULFILLMENT_ORDER,
                        is_primary=True,
                        **address_fields,
                    )
                    address = await self.address_repository.create(address)
                    order.ship_to_address_id = address.id

        return await self.repository.update(order)

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
