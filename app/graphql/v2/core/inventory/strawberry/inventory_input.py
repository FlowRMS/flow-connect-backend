from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.inventory import (
    ABCClass,
    InventoryItem,
    InventoryItemStatus,
    OwnershipType,
)
from commons.db.v6.warehouse.inventory.inventory import Inventory

from app.core.strawberry.inputs import BaseInputGQL
from app.core.utils.datetime import make_naive


@strawberry.input
class CreateInventoryInput(BaseInputGQL[Inventory]):
    warehouse_id: UUID
    product_id: UUID

    def to_orm_model(self) -> Inventory:
        return Inventory(
            warehouse_id=self.warehouse_id,
            product_id=self.product_id,
        )


@strawberry.input
class UpdateInventoryInput:
    id: UUID
    abc_class: ABCClass | None = strawberry.UNSET
    ownership_type: OwnershipType | None = strawberry.UNSET


@strawberry.input
class AddInventoryItemInput(BaseInputGQL[InventoryItem]):
    inventory_id: UUID
    location_id: UUID | None = None
    quantity: Decimal = Decimal(0)
    lot_number: str | None = None
    status: InventoryItemStatus = InventoryItemStatus.AVAILABLE
    received_date: datetime | None = None

    def to_orm_model(self) -> InventoryItem:
        return InventoryItem(
            inventory_id=self.inventory_id,
            location_id=self.location_id,
            quantity=self.quantity,
            lot_number=self.lot_number,
            status=self.status,
            received_date=make_naive(self.received_date),
        )


@strawberry.input
class UpdateInventoryItemInput:
    id: UUID
    location_id: UUID | None = strawberry.UNSET
    quantity: Decimal | None = strawberry.UNSET
    lot_number: str | None = strawberry.UNSET
    status: InventoryItemStatus | None = strawberry.UNSET
    received_date: datetime | None = strawberry.UNSET
