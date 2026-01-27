from datetime import UTC, datetime
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.fulfillment import (
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentOrder,
    FulfillmentOrderStatus,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.fulfillment.processors import (
    UpdateOrderOnFulfillmentProcessor,
)
from app.graphql.v2.core.fulfillment.repositories import (
    FulfillmentActivityRepository,
    FulfillmentOrderRepository,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    CompleteShippingInput,
)


class FulfillmentShippingService:
    def __init__(
        self,
        order_repository: FulfillmentOrderRepository,
        activity_repository: FulfillmentActivityRepository,
        update_order_processor: UpdateOrderOnFulfillmentProcessor,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.order_repository = order_repository
        self.activity_repository = activity_repository
        self.update_order_processor = update_order_processor
        self.auth_info = auth_info

    async def complete_shipping(
        self,
        order_id: UUID,
        input: CompleteShippingInput,
    ) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.SHIPPING:
            raise ValueError("Order must be in SHIPPING status to complete")

        # Update shipping details
        if input.tracking_numbers:
            order.tracking_numbers = input.tracking_numbers
        if input.bol_number:
            order.bol_number = input.bol_number
        if input.pro_number:
            order.pro_number = input.pro_number

        # Capture signature if provided
        if input.signature:
            order.pickup_signature = input.signature
            order.pickup_timestamp = datetime.now(UTC).replace(tzinfo=None)
        if input.driver_name:
            order.driver_name = input.driver_name
        if input.pickup_customer_name:
            order.pickup_customer_name = input.pickup_customer_name

        order.status = FulfillmentOrderStatus.SHIPPED
        order.ship_confirmed_at = datetime.now(UTC).replace(tzinfo=None)

        # Update shipped quantities
        for line_item in order.line_items:
            line_item.shipped_qty = line_item.picked_qty

        order = await self.order_repository.update(order)

        # Update parent Order/OrderDetail statuses
        _ = await self.update_order_processor.process_fulfillment_shipped(order)

        _ = await self._log_activity(
            order.id, FulfillmentActivityType.SHIPPED, "Shipment completed"
        )

        if input.signature:
            _ = await self._log_activity(
                order.id,
                FulfillmentActivityType.SIGNATURE_CAPTURED,
                f"Signature captured from {input.driver_name or input.pickup_customer_name}",
            )

        return order

    async def mark_delivered(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status not in [
            FulfillmentOrderStatus.SHIPPED,
            FulfillmentOrderStatus.COMMUNICATED,
        ]:
            raise ValueError("Order must be SHIPPED or COMMUNICATED to mark delivered")

        order.status = FulfillmentOrderStatus.DELIVERED
        order.delivered_at = datetime.now(UTC).replace(tzinfo=None)

        order = await self.order_repository.update(order)
        _ = await self._log_activity(
            order.id, FulfillmentActivityType.DELIVERED, "Delivery confirmed"
        )
        return order

    async def mark_communicated(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.SHIPPED:
            raise ValueError("Order must be SHIPPED to mark communicated")

        order.status = FulfillmentOrderStatus.COMMUNICATED

        order = await self.order_repository.update(order)
        return order

    async def _get_order_or_raise(self, order_id: UUID) -> FulfillmentOrder:
        order = await self.order_repository.get_with_relations(order_id)
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
