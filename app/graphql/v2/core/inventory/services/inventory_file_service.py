import base64
import csv
import io
from decimal import Decimal, InvalidOperation
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.warehouse.inventory.inventory import Inventory
from commons.db.v6.warehouse.inventory.inventory_item import (
    InventoryItem,
    InventoryItemStatus,
)

from app.graphql.v2.core.inventory.repositories.inventory_item_repository import (
    InventoryItemRepository,
)
from app.graphql.v2.core.inventory.repositories.inventory_repository import (
    InventoryRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.warehouses.repositories.warehouse_location_repository import (
    WarehouseLocationRepository,
)


from app.graphql.v2.core.inventory.services.inventory_item_service import (
    InventoryItemService,
)

class InventoryFileService:
    def __init__(
        self,
        inventory_repository: InventoryRepository,
        inventory_item_repository: InventoryItemRepository,
        products_repository: ProductsRepository,
        location_repository: WarehouseLocationRepository,
        item_service: InventoryItemService,
        auth_info: AuthInfo,
    ) -> None:
        self.inventory_repository = inventory_repository
        self.item_repository = inventory_item_repository
        self.products_repository = products_repository
        self.location_repository = location_repository
        self.item_service = item_service
        self.auth_info = auth_info

    async def export_inventory_csv(self, warehouse_id: UUID) -> str:
        inventory_list = await self.inventory_repository.find_by_warehouse(
            warehouse_id=warehouse_id,
        )

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "SKU",
            "Product Name",
            "Location",
            "Quantity",
            "Status",
            "Lot Number"
        ])
        writer.writeheader()

        for inventory in inventory_list:
            if not inventory.items:
                continue

            for item in inventory.items:
                product_name = "N/A"
                sku = "N/A"
                if inventory.product:
                    product_name = inventory.product.description or "N/A"
                    sku = inventory.product.factory_part_number
                
                location_name = "N/A"
                if item.location:
                    location_name = item.location.name
                
                writer.writerow({
                    "SKU": sku,
                    "Product Name": product_name,
                    "Location": location_name,
                    "Quantity": str(item.quantity),
                    "Status": item.status.name,
                    "Lot Number": item.lot_number or ""
                })

        csv_content = output.getvalue()
        return base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")

    async def import_inventory_csv(
        self, warehouse_id: UUID, file_content: str
    ) -> dict[str, int]:
        try:
            decoded_content = base64.b64decode(file_content).decode("utf-8")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid Base64 encoded file content: {e}") from e

        reader = csv.DictReader(io.StringIO(decoded_content))
        
        stats = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "errors": 0,
            "skipped": 0
        }

        for row in reader:
            stats["processed"] += 1
            sku = row.get("SKU", "").strip()
            location_name = row.get("Location", "").strip()
            quantity_str = row.get("Quantity", "0").strip()
            status_str = row.get("Status", "AVAILABLE").strip().upper()
            lot_number = row.get("Lot Number", "").strip() or None

            if not sku:
                stats["skipped"] += 1
                continue

            try:
                quantity = Decimal(quantity_str)
            except (ValueError, InvalidOperation):
                stats["errors"] += 1
                continue

            # 1. Find Product
            product = await self.products_repository.find_by_factory_part_number(sku)
            if not product:
                stats["errors"] += 1
                continue

            # 2. Find Location
            location = None
            if location_name and location_name != "N/A":
                location = await self.location_repository.find_by_name(
                    warehouse_id, location_name
                )
                if not location:
                    stats["errors"] += 1
                    continue
            
            # 3. Find/Create Inventory
            inventory = await self.inventory_repository.find_by_product_id(
                warehouse_id, product.id
            )
            
            if not inventory:
                inventory = await self.inventory_repository.create(Inventory(
                    warehouse_id=warehouse_id,
                    product_id=product.id,
                    total_quantity=Decimal(0),
                    available_quantity=Decimal(0),
                ))

            status_enum = InventoryItemStatus.AVAILABLE
            try:
                status_enum = InventoryItemStatus[status_str]
            except KeyError:
                pass  # Use default

            existing_items = await self.item_repository.find_by_inventory_id(inventory.id)
            target_item = self._find_matching_item(
                existing_items,
                location.id if location else None,
                lot_number,
                status_enum,
            )
            
            if target_item:
                new_qty = target_item.quantity + quantity
                await self.item_service.update_item(
                    item_id=target_item.id,
                    quantity=new_qty
                )
                stats["updated"] += 1
            else:
                new_item = InventoryItem(
                    inventory_id=inventory.id,
                    location_id=location.id if location else None,
                    quantity=quantity,
                    status=status_enum,
                    lot_number=lot_number
                )
                await self.item_service.add_item(new_item)
                stats["created"] += 1

        return stats

    def _find_matching_item(
        self,
        items: list[InventoryItem],
        location_id: UUID | None,
        lot_number: str | None,
        status: InventoryItemStatus,
    ) -> InventoryItem | None:
        for item in items:
            if item.location_id != location_id:
                continue
            if item.lot_number != lot_number:
                continue
            if item.status != status:
                continue
            return item
        return None
