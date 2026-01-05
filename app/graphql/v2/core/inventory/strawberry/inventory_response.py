from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.inventory import ABCClass, Inventory, OwnershipType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.inventory.strawberry.inventory_item_response import (
    InventoryItemResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductResponse


@strawberry.type
class InventoryLiteResponse(DTOMixin[Inventory]):
    id: UUID
    product_id: UUID
    warehouse_id: UUID
    total_quantity: Decimal
    available_quantity: Decimal
    reserved_quantity: Decimal
    picking_quantity: Decimal
    ownership_type: OwnershipType
    abc_class: ABCClass | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, model: Inventory) -> Self:
        return cls(
            id=model.id,
            product_id=model.product_id,
            warehouse_id=model.warehouse_id,
            total_quantity=model.total_quantity,
            available_quantity=model.available_quantity,
            reserved_quantity=model.reserved_quantity,
            picking_quantity=model.picking_quantity,
            ownership_type=model.ownership_type,
            abc_class=model.abc_class,
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
            warehouse_id=model.warehouse_id,
            total_quantity=model.total_quantity,
            available_quantity=model.available_quantity,
            reserved_quantity=model.reserved_quantity,
            picking_quantity=model.picking_quantity,
            ownership_type=model.ownership_type,
            abc_class=model.abc_class,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @strawberry.field
    async def items(self) -> list[InventoryItemResponse]:
        items = await self._instance.awaitable_attrs.items
        return InventoryItemResponse.from_orm_model_list(items)

    @strawberry.field
    async def product(self) -> ProductResponse:
        return ProductResponse.from_orm_model(
            await self._instance.awaitable_attrs.product
        )
