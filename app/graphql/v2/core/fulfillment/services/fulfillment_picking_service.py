from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.fulfillment import (
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentOrder,
    FulfillmentOrderLineItem,
    FulfillmentOrderStatus,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.fulfillment.repositories import (
    FulfillmentActivityRepository,
    FulfillmentLineRepository,
    FulfillmentOrderRepository,
)


class FulfillmentPickingService:
    def __init__(
        self,
        order_repository: FulfillmentOrderRepository,
        line_repository: FulfillmentLineRepository,
        activity_repository: FulfillmentActivityRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.order_repository = order_repository
        self.line_repository = line_repository
        self.activity_repository = activity_repository
        self.auth_info = auth_info

    async def start_picking(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.RELEASED:
            raise ValueError("Order must be in RELEASED status to start picking")

        order.status = FulfillmentOrderStatus.PICKING
        order.pick_started_at = datetime.now(timezone.utc)

        order = await self.order_repository.update(order)
        await self._log_activity(
            order.id, FulfillmentActivityType.PICK_STARTED, "Picking started"
        )
        return order

    async def update_picked_quantity(
        self,
        line_item_id: UUID,
        quantity: Decimal,
        notes: str | None = None,
    ) -> FulfillmentOrderLineItem:
        line_item = await self.line_repository.get_with_relations(line_item_id)
        if not line_item:
            raise NotFoundError(f"Line item {line_item_id} not found")

        line_item.picked_qty = quantity
        if notes:
            line_item.notes = notes

        return await self.line_repository.update(line_item)

    async def complete_picking(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.PICKING:
            raise ValueError("Order must be in PICKING status to complete")

        # Check if all items are picked
        all_picked = all(
            item.picked_qty >= item.ordered_qty - item.backorder_qty
            for item in order.line_items
        )

        if not all_picked:
            raise ValueError("Not all items have been picked")

        order.status = FulfillmentOrderStatus.PACKING
        order.pick_completed_at = datetime.now(timezone.utc)

        order = await self.order_repository.update(order)
        await self._log_activity(
            order.id, FulfillmentActivityType.PICK_COMPLETED, "Picking completed"
        )
        return order

    async def report_discrepancy(
        self,
        line_item_id: UUID,
        actual_quantity: Decimal,
        reason: str,
    ) -> FulfillmentOrder:
        line_item = await self.line_repository.get_with_relations(line_item_id)
        if not line_item:
            raise NotFoundError(f"Line item {line_item_id} not found")

        shortage = line_item.ordered_qty - actual_quantity
        if shortage > 0:
            line_item.backorder_qty = shortage
            line_item.short_reason = reason
            line_item.allocated_qty = actual_quantity

            await self.line_repository.update(line_item)

            order = await self._get_order_or_raise(line_item.fulfillment_order_id)
            order.has_backorder_items = True
            order.status = FulfillmentOrderStatus.BACKORDER_REVIEW
            order = await self.order_repository.update(order)

            await self._log_activity(
                order.id,
                FulfillmentActivityType.BACKORDER_REPORTED,
                f"Inventory discrepancy reported: {reason}",
                {"line_item_id": str(line_item_id), "shortage": str(shortage)},
            )
            return order

        return await self._get_order_or_raise(line_item.fulfillment_order_id)

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
