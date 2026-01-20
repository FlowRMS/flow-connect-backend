from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.fulfillment import (
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentOrder,
    FulfillmentOrderStatus,
    PackingBox,
    PackingBoxItem,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.fulfillment.repositories import (
    FulfillmentActivityRepository,
    FulfillmentOrderRepository,
    PackingBoxItemRepository,
    PackingBoxRepository,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    CreatePackingBoxInput,
    UpdatePackingBoxInput,
)


class FulfillmentPackingService:
    def __init__(
        self,
        order_repository: FulfillmentOrderRepository,
        box_repository: PackingBoxRepository,
        box_item_repository: PackingBoxItemRepository,
        activity_repository: FulfillmentActivityRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.order_repository = order_repository
        self.box_repository = box_repository
        self.box_item_repository = box_item_repository
        self.activity_repository = activity_repository
        self.auth_info = auth_info

    async def add_box(
        self,
        fulfillment_order_id: UUID,
        input: CreatePackingBoxInput,
    ) -> PackingBox:
        box = input.to_orm_model()
        box.fulfillment_order_id = fulfillment_order_id
        box.box_number = await self.box_repository.get_next_box_number(
            fulfillment_order_id
        )
        created_box = await self.box_repository.create(box)
        # Fetch with relationships to avoid lazy loading issues
        result = await self.box_repository.get_with_items(created_box.id)
        if not result:
            raise NotFoundError(f"Packing box {created_box.id} not found after creation")
        return result

    async def update_box(
        self,
        box_id: UUID,
        input: UpdatePackingBoxInput,
    ) -> PackingBox:
        box = await self.box_repository.get_with_items(box_id)
        if not box:
            raise NotFoundError(f"Packing box {box_id} not found")

        box.container_type_id = input.optional_field(
            input.container_type_id, box.container_type_id
        )
        box.length = input.optional_field(input.length, box.length)
        box.width = input.optional_field(input.width, box.width)
        box.height = input.optional_field(input.height, box.height)
        box.weight = input.optional_field(input.weight, box.weight)
        box.tracking_number = input.optional_field(
            input.tracking_number, box.tracking_number
        )

        await self.box_repository.update(box)
        # Fetch with relationships to avoid lazy loading issues
        result = await self.box_repository.get_with_items(box_id)
        if not result:
            raise NotFoundError(f"Packing box {box_id} not found after update")
        return result

    async def delete_box(self, box_id: UUID) -> bool:
        box = await self.box_repository.get_with_items(box_id)
        if not box:
            raise NotFoundError(f"Packing box {box_id} not found")
        return await self.box_repository.delete(box_id)

    async def assign_item_to_box(
        self,
        box_id: UUID,
        line_item_id: UUID,
        quantity: Decimal,
    ) -> PackingBox:
        box = await self.box_repository.get_with_items(box_id)
        if not box:
            raise NotFoundError(f"Packing box {box_id} not found")

        # Check if already assigned
        existing = await self.box_item_repository.get_by_box_and_line_item(
            box_id, line_item_id
        )
        if existing:
            existing.quantity = quantity
            _ = await self.box_item_repository.update(existing)
        else:
            item = PackingBoxItem()
            item.fulfillment_line_item_id = line_item_id
            item.quantity = quantity
            item.packing_box_id = box_id
            _ = await self.box_item_repository.create(item)

        result = await self.box_repository.get_with_items(box_id)
        if not result:
            raise NotFoundError(f"Packing box {box_id} not found")
        return result

    async def remove_item_from_box(
        self,
        box_id: UUID,
        line_item_id: UUID,
    ) -> PackingBox:
        existing = await self.box_item_repository.get_by_box_and_line_item(
            box_id, line_item_id
        )
        if existing:
            _ = await self.box_item_repository.delete(existing.id)
        result = await self.box_repository.get_with_items(box_id)
        if not result:
            raise NotFoundError(f"Packing box {box_id} not found")
        return result

    async def complete_packing(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.PACKING:
            raise ValueError("Order must be in PACKING status to complete")

        order.status = FulfillmentOrderStatus.SHIPPING
        order.pack_completed_at = datetime.now(UTC).replace(tzinfo=None)

        order = await self.order_repository.update(order)
        _ = await self._log_activity(
            order.id, FulfillmentActivityType.PACK_COMPLETED, "Packing completed"
        )
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
