from datetime import datetime
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
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_input import (
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
        return await self.box_repository.create(box)

    async def update_box(
        self,
        box_id: UUID,
        input: UpdatePackingBoxInput,
    ) -> PackingBox:
        import strawberry

        box = await self.box_repository.get_with_items(box_id)
        if not box:
            raise NotFoundError(f"Packing box {box_id} not found")

        if input.container_type_id is not strawberry.UNSET:
            box.container_type_id = input.container_type_id
        if input.length is not strawberry.UNSET:
            box.length = input.length
        if input.width is not strawberry.UNSET:
            box.width = input.width
        if input.height is not strawberry.UNSET:
            box.height = input.height
        if input.weight is not strawberry.UNSET:
            box.weight = input.weight
        if input.tracking_number is not strawberry.UNSET:
            box.tracking_number = input.tracking_number

        return await self.box_repository.update(box)

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
            await self.box_item_repository.update(existing)
        else:
            item = PackingBoxItem(
                fulfillment_line_item_id=line_item_id,
                quantity=quantity,
            )
            item.packing_box_id = box_id
            await self.box_item_repository.create(item)

        return await self.box_repository.get_with_items(box_id)

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
        return await self.box_repository.get_with_items(box_id)

    async def complete_packing(self, order_id: UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.PACKING:
            raise ValueError("Order must be in PACKING status to complete")

        order.status = FulfillmentOrderStatus.SHIPPING
        order.pack_completed_at = datetime.utcnow()

        order = await self.order_repository.update(order)
        await self._log_activity(
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
