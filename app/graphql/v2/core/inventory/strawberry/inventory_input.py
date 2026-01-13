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
class UpdateInventoryInput(BaseInputGQL[Inventory]):
    id: UUID
    abc_class: ABCClass | None = strawberry.UNSET
    ownership_type: OwnershipType | None = strawberry.UNSET

    def to_orm_model(self) -> Inventory:
        inventory = Inventory(
            warehouse_id=UUID(int=0),
            product_id=UUID(int=0),
        )
        inventory.id = self.id
        
        if self.abc_class != strawberry.UNSET:
            inventory.abc_class = self.abc_class
            
        if self.ownership_type != strawberry.UNSET and self.ownership_type is not None:
             inventory.ownership_type = self.ownership_type
             
        return inventory


@strawberry.input
class AddInventoryItemInput(BaseInputGQL[InventoryItem]):
    inventory_id: UUID
    location_id: UUID | None = None
    quantity: Decimal = Decimal(0)
    lot_number: str | None = None
    status: InventoryItemStatus = InventoryItemStatus.AVAILABLE
    received_date: datetime | None = None

    def to_orm_model(self) -> InventoryItem:
        received_date = self.received_date
        if received_date and received_date.tzinfo:
            received_date = received_date.replace(tzinfo=None)

        item = InventoryItem(
            inventory_id=self.inventory_id,
            location_id=self.location_id,
            quantity=self.quantity,
            lot_number=self.lot_number,
            status=self.status,
            received_date=received_date,
        )

        return item


@strawberry.input
class UpdateInventoryItemInput(BaseInputGQL[InventoryItem]):
    id: UUID
    location_id: UUID | None = strawberry.UNSET
    quantity: Decimal | None = strawberry.UNSET
    lot_number: str | None = strawberry.UNSET
    status: InventoryItemStatus | None = strawberry.UNSET
    received_date: datetime | None = strawberry.UNSET

    def to_orm_model(self) -> InventoryItem:
        # Note: This is an update input, so we return a model with only the fields that are set.
        # In practice, this method might not be used directly for updates if the service handles it field-by-field.
        # But we implement it to satisfy the BaseInputGQL contract.
        
        # Use dummy values for required fields that are not present in update input
        item = InventoryItem(
            inventory_id=UUID(int=0),
            quantity=self.quantity if self.quantity is not strawberry.UNSET and self.quantity is not None else Decimal(0),
            status=self.status if self.status != strawberry.UNSET and self.status is not None else InventoryItemStatus.AVAILABLE,
        )
        item.id = self.id
        
        if self.quantity != strawberry.UNSET and self.quantity is not None:
            item.quantity = self.quantity
            
        if self.status != strawberry.UNSET and self.status is not None:
            item.status = self.status
        
        if self.location_id != strawberry.UNSET:
            item.location_id = self.location_id
        if self.lot_number != strawberry.UNSET:
            item.lot_number = self.lot_number
        if self.received_date != strawberry.UNSET:
            received_date = self.received_date
            if received_date and received_date.tzinfo:
                received_date = received_date.replace(tzinfo=None)
            item.received_date = received_date
            
        return item
