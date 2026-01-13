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
from app.graphql.v2.core.products.strawberry.product_response import (
    ProductLiteResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.inject import inject
from aioinject import Injected


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
    def items(self) -> list[InventoryItemResponse]:
        return InventoryItemResponse.from_orm_model_list(self._instance.items)

    @strawberry.field
    @inject
    async def product(
        self, product_service: Injected[ProductService]
    ) -> ProductLiteResponse:
        product = await product_service.get_by_id(self.product_id)
        if not product:
            # Should conceptually not happen if FK is valid, but handle gracefully
            raise Exception(f"Product {self.product_id} not found")
        return ProductLiteResponse.from_orm_model(product)

    @strawberry.field
    @inject
    async def factory(
        self, product_service: Injected[ProductService]
    ) -> FactoryLiteResponse | None:
        try:
             product = await product_service.get_by_id(self.product_id)
             if product and product.factory:
                 return FactoryLiteResponse.from_orm_model(product.factory)
        except Exception:
             # Return None if product or factory not found to avoid crashing
             pass
        return None
