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


class FulfillmentBackorderService:
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

    async def get_backorder_items(
        self,
        fulfillment_order_id: UUID,
    ) -> list[FulfillmentOrderLineItem]:
        """Get all line items with backorder quantities."""
        order = await self._get_order_or_raise(fulfillment_order_id)
        return [item for item in order.line_items if item.backorder_qty > 0]

    async def mark_manufacturer_fulfilled(
        self,
        fulfillment_order_id: UUID,
        line_item_ids: list[UUID],
    ) -> FulfillmentOrder:
        """Mark line items as being fulfilled by manufacturer."""
        order = await self._get_order_or_raise(fulfillment_order_id)

        for line_item in order.line_items:
            if line_item.id in line_item_ids:
                line_item.fulfilled_by_manufacturer = True
                line_item.manufacturer_fulfillment_status = "PENDING_MANUFACTURER"
                _ = await self.line_repository.update(line_item)

        _ = await self._log_activity(
            fulfillment_order_id,
            FulfillmentActivityType.NOTE_ADDED,
            f"Marked {len(line_item_ids)} item(s) for manufacturer fulfillment",
            {"line_item_ids": [str(id) for id in line_item_ids]},
        )

        # Check if we can continue with remaining items
        await self._update_backorder_status(order)

        result = await self.order_repository.get_with_relations(fulfillment_order_id)
        if not result:
            raise NotFoundError(f"Fulfillment order {fulfillment_order_id} not found")
        return result

    async def split_line_item(
        self,
        line_item_id: UUID,
        warehouse_qty: Decimal,
        manufacturer_qty: Decimal,
    ) -> FulfillmentOrderLineItem:
        """Split a line item between warehouse and manufacturer fulfillment."""
        line_item = await self.line_repository.get_with_relations(line_item_id)
        if not line_item:
            raise NotFoundError(f"Line item {line_item_id} not found")

        total_qty = warehouse_qty + manufacturer_qty
        if total_qty > line_item.ordered_qty:
            raise ValueError(
                f"Split quantities ({total_qty}) exceed ordered quantity ({line_item.ordered_qty})"
            )

        # Update the line item
        line_item.allocated_qty = warehouse_qty
        line_item.backorder_qty = manufacturer_qty

        if manufacturer_qty > 0:
            line_item.fulfilled_by_manufacturer = True
            line_item.manufacturer_fulfillment_status = "PENDING_MANUFACTURER"

        line_item = await self.line_repository.update(line_item)

        _ = await self._log_activity(
            line_item.fulfillment_order_id,
            FulfillmentActivityType.NOTE_ADDED,
            f"Split order: {warehouse_qty} from warehouse, {manufacturer_qty} from manufacturer",
            {
                "line_item_id": str(line_item_id),
                "warehouse_qty": str(warehouse_qty),
                "manufacturer_qty": str(manufacturer_qty),
            },
        )

        # Update order status if needed
        order = await self._get_order_or_raise(line_item.fulfillment_order_id)
        await self._update_backorder_status(order)

        return line_item

    async def cancel_backorder_items(
        self,
        fulfillment_order_id: UUID,
        line_item_ids: list[UUID],
        reason: str,
    ) -> FulfillmentOrder:
        """Cancel backorder items and adjust quantities."""
        order = await self._get_order_or_raise(fulfillment_order_id)

        cancelled_count = 0
        for line_item in order.line_items:
            if line_item.id in line_item_ids:
                # Reduce ordered qty by backorder amount
                line_item.ordered_qty = line_item.ordered_qty - line_item.backorder_qty
                line_item.backorder_qty = Decimal("0")
                line_item.short_reason = reason
                _ = await self.line_repository.update(line_item)
                cancelled_count += 1

        _ = await self._log_activity(
            fulfillment_order_id,
            FulfillmentActivityType.NOTE_ADDED,
            f"Cancelled backorder for {cancelled_count} item(s): {reason}",
            {
                "line_item_ids": [str(id) for id in line_item_ids],
                "reason": reason,
            },
        )

        # Check if entire order should be cancelled
        updated_order = await self.order_repository.get_with_relations(
            fulfillment_order_id
        )
        if not updated_order:
            raise NotFoundError(f"Fulfillment order {fulfillment_order_id} not found")

        total_ordered = sum(item.ordered_qty for item in updated_order.line_items)

        if total_ordered == 0:
            updated_order.status = FulfillmentOrderStatus.CANCELLED
            updated_order.hold_reason = f"All items cancelled: {reason}"
            _ = await self.order_repository.update(updated_order)
            _ = await self._log_activity(
                fulfillment_order_id,
                FulfillmentActivityType.CANCELLED,
                "Order cancelled - all items removed",
            )
        else:
            # Update backorder status
            await self._update_backorder_status(updated_order)

        result = await self.order_repository.get_with_relations(fulfillment_order_id)
        if not result:
            raise NotFoundError(f"Fulfillment order {fulfillment_order_id} not found")
        return result

    async def link_shipment_request(
        self,
        fulfillment_order_id: UUID,
        line_item_ids: list[UUID],
        shipment_request_id: UUID,
    ) -> FulfillmentOrder:
        """Link line items to a shipment request for inventory replenishment."""
        order = await self._get_order_or_raise(fulfillment_order_id)

        linked_count = 0
        for line_item in order.line_items:
            if line_item.id in line_item_ids:
                line_item.linked_shipment_request_id = shipment_request_id
                _ = await self.line_repository.update(line_item)
                linked_count += 1

        # Update hold reason
        order.hold_reason = "Pending inventory from shipment request"
        _ = await self.order_repository.update(order)

        _ = await self._log_activity(
            fulfillment_order_id,
            FulfillmentActivityType.NOTE_ADDED,
            f"Linked {linked_count} item(s) to shipment request {shipment_request_id}",
            {
                "line_item_ids": [str(id) for id in line_item_ids],
                "shipment_request_id": str(shipment_request_id),
            },
        )

        result = await self.order_repository.get_with_relations(fulfillment_order_id)
        if not result:
            raise NotFoundError(f"Fulfillment order {fulfillment_order_id} not found")
        return result

    async def resolve_backorder(
        self,
        fulfillment_order_id: UUID,
    ) -> FulfillmentOrder:
        """Resolve backorder status and continue fulfillment."""
        order = await self._get_order_or_raise(fulfillment_order_id)

        if order.status != FulfillmentOrderStatus.BACKORDER_REVIEW:
            raise ValueError("Order is not in backorder review status")

        # Check if all backorder items have been handled
        unhandled_backorders = [
            item
            for item in order.line_items
            if item.backorder_qty > 0 and not item.fulfilled_by_manufacturer
        ]

        if unhandled_backorders:
            raise ValueError(
                f"{len(unhandled_backorders)} items still have unresolved backorders"
            )

        # Move back to picking status
        order.status = FulfillmentOrderStatus.PICKING
        order.has_backorder_items = False
        order = await self.order_repository.update(order)

        _ = await self._log_activity(
            fulfillment_order_id,
            FulfillmentActivityType.NOTE_ADDED,
            "Backorder resolved - resuming fulfillment",
        )

        return order

    async def _update_backorder_status(self, order: FulfillmentOrder) -> None:
        """Update order backorder status based on line items."""
        has_unresolved_backorders = any(
            item.backorder_qty > 0 and not item.fulfilled_by_manufacturer
            for item in order.line_items
        )

        order.has_backorder_items = has_unresolved_backorders

        if (
            not has_unresolved_backorders
            and order.status == FulfillmentOrderStatus.BACKORDER_REVIEW
        ):
            # Can continue with fulfillment
            order.status = FulfillmentOrderStatus.PICKING
            _ = await self.order_repository.update(order)

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
