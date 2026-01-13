from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from commons.db.v6 import Delivery, DeliveryItem, DeliveryItemReceipt
from commons.db.v6.warehouse.deliveries.delivery_enums import (
    DeliveryReceiptType,
    DeliveryStatus,
)
from commons.db.v6.warehouse.inventory.inventory import Inventory
from commons.db.v6.warehouse.inventory.inventory_item import (
    InventoryItem,
    InventoryItemStatus,
)
from loguru import logger

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.deliveries_repository import (
    DeliveriesRepository,
)
from app.graphql.v2.core.inventory.repositories.inventory_repository import (
    InventoryRepository,
)
from app.graphql.v2.core.inventory.services.inventory_item_service import (
    InventoryItemService,
)


class DeliveryInventorySyncService:
    def __init__(
        self,
        deliveries_repository: DeliveriesRepository,
        inventory_repository: InventoryRepository,
        inventory_item_service: InventoryItemService,
    ) -> None:
        super().__init__()
        self.deliveries_repository = deliveries_repository
        self.inventory_repository = inventory_repository
        self.inventory_item_service = inventory_item_service

    async def sync_received_delivery(self, delivery_id: UUID) -> bool:
        delivery = await self.deliveries_repository.get_with_relations(delivery_id)
        if not delivery:
            raise NotFoundError(f"Delivery with id {delivery_id} not found")

        if delivery.inventory_synced_at is not None:
            return False

        if delivery.status != DeliveryStatus.RECEIVED:
            return False

        for item in delivery.items:
            if item.receipts:
                await self._sync_item_receipts(delivery, item)
            else:
                await self._sync_item_totals(delivery, item)

        delivery.inventory_synced_at = datetime.now(timezone.utc)
        _ = await self.deliveries_repository.update(delivery)
        return True

    async def _sync_item_receipts(
        self,
        delivery: Delivery,
        item: DeliveryItem,
    ) -> None:
        inventory = await self._get_or_create_inventory(
            delivery=delivery,
            product_id=item.product_id,
        )
        for receipt in item.receipts:
            if receipt.receipt_type not in {
                DeliveryReceiptType.RECEIPT,
                DeliveryReceiptType.ADJUSTMENT,
            }:
                continue

            await self._create_inventory_items(
                inventory=inventory,
                receipt=receipt,
                received_at=receipt.received_at or delivery.received_at,
            )

    async def _sync_item_totals(
        self,
        delivery: Delivery,
        item: DeliveryItem,
    ) -> None:
        if item.received_qty <= 0 and item.damaged_qty <= 0:
            return

        inventory = await self._get_or_create_inventory(
            delivery=delivery,
            product_id=item.product_id,
        )
        receipt = DeliveryItemReceipt(
            delivery_item_id=item.id,
            received_qty=item.received_qty,
            damaged_qty=item.damaged_qty,
            location_id=None,
            received_at=delivery.received_at,
        )
        await self._create_inventory_items(
            inventory=inventory,
            receipt=receipt,
            received_at=delivery.received_at,
        )

    async def _create_inventory_items(
        self,
        inventory: Inventory,
        receipt: DeliveryItemReceipt,
        received_at: datetime | None,
    ) -> None:
        received_at = self._normalize_received_date(received_at)
        if receipt.received_qty > 0:
            await self._create_inventory_item(
                inventory=inventory,
                quantity=receipt.received_qty,
                status=InventoryItemStatus.AVAILABLE,
                location_id=receipt.location_id,
                received_at=received_at,
            )
        if receipt.damaged_qty > 0:
            await self._create_inventory_item(
                inventory=inventory,
                quantity=receipt.damaged_qty,
                status=InventoryItemStatus.DAMAGED,
                location_id=receipt.location_id,
                received_at=received_at,
            )

    async def _create_inventory_item(
        self,
        inventory: Inventory,
        quantity: int,
        status: InventoryItemStatus,
        location_id: UUID | None,
        received_at: datetime | None,
    ) -> None:
        item = InventoryItem(
            inventory_id=inventory.id,
            location_id=location_id,
            quantity=Decimal(quantity),
            status=status,
            received_date=received_at,
        )
        _ = await self.inventory_item_service.add_item(item)
        logger.info(
            "Added inventory item for delivery sync: inventory_id={}, status={}, qty={}",
            inventory.id,
            status.name,
            quantity,
        )

    def _normalize_received_date(self, received_at: datetime | None) -> datetime | None:
        if not received_at:
            return None
        if received_at.tzinfo is None:
            return received_at
        return received_at.astimezone(timezone.utc).replace(tzinfo=None)

    async def _get_or_create_inventory(
        self,
        delivery: Delivery,
        product_id: UUID,
    ) -> Inventory:
        inventory = await self.inventory_repository.find_by_product_id(
            warehouse_id=delivery.warehouse_id,
            product_id=product_id,
        )
        if inventory:
            return inventory

        return await self.inventory_repository.create(
            Inventory(
                warehouse_id=delivery.warehouse_id,
                product_id=product_id,
            )
        )
