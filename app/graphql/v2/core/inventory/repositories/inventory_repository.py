from uuid import UUID

from commons.db.v6.core.products.product import Product
from commons.db.v6.warehouse.inventory import ABCClass, OwnershipType
from commons.db.v6.warehouse.inventory.inventory import Inventory
from commons.db.v6.warehouse.inventory.inventory_item import InventoryItem
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET
from app.core.context_wrapper import ContextWrapper
from app.errors.common_errors import NotFoundError
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.inventory.strawberry.inventory_stats_response import (
    InventoryStatsResponse,
)


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Inventory,
        )

    def _default_options(self) -> list:
        return [
            joinedload(Inventory.items).joinedload(InventoryItem.location),
            joinedload(Inventory.product).joinedload(Product.factory),
        ]

    async def get_by_id(self, entity_id: UUID | str) -> Inventory | None:
        if isinstance(entity_id, str):
            entity_id = UUID(entity_id)
        stmt = (
            select(Inventory)
            .where(Inventory.id == entity_id)
            .options(*self._default_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_warehouse(
        self,
        warehouse_id: UUID,
        factory_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[Inventory]:
        stmt = (
            select(Inventory)
            .join(Inventory.product)
            .where(Inventory.warehouse_id == warehouse_id)
            .options(
                joinedload(Inventory.items).joinedload(InventoryItem.location),
                contains_eager(Inventory.product).joinedload(Product.factory),
            )
            .limit(limit)
            .offset(offset)
        )

        if factory_id:
            stmt = stmt.where(Product.factory_id == factory_id)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (Product.description.ilike(search_pattern))
                | (Product.factory_part_number.ilike(search_pattern))
            )

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_product_id(
        self, warehouse_id: UUID, product_id: UUID
    ) -> Inventory | None:
        stmt = (
            select(Inventory)
            .where(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == product_id,
            )
            .join(Inventory.product)
            .options(
                joinedload(Inventory.items),
                contains_eager(Inventory.product),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_stats_by_warehouse(
        self, warehouse_id: UUID
    ) -> InventoryStatsResponse:
        stmt = select(
            func.count(Inventory.id).label("total_products"),
            func.coalesce(func.sum(Inventory.total_quantity), 0).label(
                "total_quantity"
            ),
            func.coalesce(func.sum(Inventory.available_quantity), 0).label(
                "available_quantity"
            ),
            func.coalesce(func.sum(Inventory.reserved_quantity), 0).label(
                "reserved_quantity"
            ),
            func.coalesce(func.sum(Inventory.picking_quantity), 0).label(
                "picking_quantity"
            ),
        ).where(Inventory.warehouse_id == warehouse_id)

        result = await self.session.execute(stmt)
        row = result.one()

        low_stock_stmt = (
            select(func.count(Inventory.id))
            .join(Inventory.product)
            .where(Inventory.warehouse_id == warehouse_id)
            .where(Product.min_order_qty.isnot(None))
            .where(Inventory.available_quantity <= Product.min_order_qty)
        )
        low_stock_result = await self.session.execute(low_stock_stmt)
        low_stock_count = low_stock_result.scalar_one()

        # Out of stock count
        out_of_stock_stmt = (
            select(func.count(Inventory.id))
            .where(Inventory.warehouse_id == warehouse_id)
            .where(Inventory.available_quantity <= 0)
        )
        out_of_stock_result = await self.session.execute(out_of_stock_stmt)
        out_of_stock_count = out_of_stock_result.scalar_one()

        # Total value (sum of total_quantity * product.unit_price)
        total_value_stmt = (
            select(
                func.coalesce(
                    func.sum(Inventory.total_quantity * Product.unit_price), 0
                )
            )
            .join(Inventory.product)
            .where(Inventory.warehouse_id == warehouse_id)
        )
        total_value_result = await self.session.execute(total_value_stmt)
        total_value = total_value_result.scalar_one()

        return InventoryStatsResponse(
            total_products=row.total_products,
            total_quantity=row.total_quantity,
            available_quantity=row.available_quantity,
            reserved_quantity=row.reserved_quantity,
            picking_quantity=row.picking_quantity,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            total_value=total_value,
        )

    async def update_fields(
        self,
        inventory_id: UUID,
        abc_class: ABCClass | None = None,
        ownership_type: OwnershipType | None = None,
    ) -> Inventory:
        inventory = await self.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundError(f"Inventory with id {inventory_id} not found")

        if abc_class is not None:
            inventory.abc_class = abc_class
        if ownership_type is not None:
            inventory.ownership_type = ownership_type

        return await self.update(inventory)

