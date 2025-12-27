from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from commons.db.v6.crm.inventory.inventory import Inventory
from app.graphql.v2.core.inventory.strawberry.inventory_item_response import (
    InventoryItemResponse,
)


@strawberry.enum
class OwnershipTypeEnum(strawberry.enum.Enum):
    CONSIGNMENT = "CONSIGNMENT"
    OWNED = "OWNED"
    THIRD_PARTY = "THIRD_PARTY"


@strawberry.enum
class ABCClassEnum(strawberry.enum.Enum):
    A = "A"
    B = "B"
    C = "C"


@strawberry.type
class InventoryLiteResponse(DTOMixin[Inventory]):
    id: UUID
    product_id: str
    product_name: str
    part_number: str
    factory_id: UUID | None
    factory_name: str | None
    warehouse_id: UUID
    total_quantity: int
    available_quantity: int
    reserved_quantity: int
    picking_quantity: int
    ownership_type: OwnershipTypeEnum
    reorder_point: int | None
    abc_class: ABCClassEnum | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, model: Inventory) -> Self:
        return cls(
            id=model.id,
            product_id=model.product_id,
            product_name=model.product_name,
            part_number=model.part_number,
            factory_id=model.factory_id,
            factory_name=model.factory_name,
            warehouse_id=model.warehouse_id,
            total_quantity=model.total_quantity,
            available_quantity=model.available_quantity,
            reserved_quantity=model.reserved_quantity,
            picking_quantity=model.picking_quantity,
            ownership_type=OwnershipTypeEnum(model.ownership_type.value),
            reorder_point=model.reorder_point,
            abc_class=ABCClassEnum(model.abc_class.value) if model.abc_class else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@strawberry.type
class InventoryResponse(InventoryLiteResponse):
    _instance: strawberry.Private[Inventory]

    @classmethod
    def from_orm_model(cls, model: Inventory) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            product_id=model.product_id,
            product_name=model.product_name,
            part_number=model.part_number,
            factory_id=model.factory_id,
            factory_name=model.factory_name,
            warehouse_id=model.warehouse_id,
            total_quantity=model.total_quantity,
            available_quantity=model.available_quantity,
            reserved_quantity=model.reserved_quantity,
            picking_quantity=model.picking_quantity,
            ownership_type=OwnershipTypeEnum(model.ownership_type.value),
            reorder_point=model.reorder_point,
            abc_class=ABCClassEnum(model.abc_class.value) if model.abc_class else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @strawberry.field
    async def items(self) -> list[InventoryItemResponse]:
        items = await self._instance.awaitable_attrs.items
        return InventoryItemResponse.from_orm_model_list(items)

    @strawberry.field
    def is_low_stock(self) -> bool:
        if self.reorder_point is None:
            return False
        return self.available_quantity <= self.reorder_point
