from uuid import UUID

from commons.db.v6.core.products.product import Product
from commons.db.v6.warehouse.inventory.inventory import Inventory
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET
from app.core.context_wrapper import ContextWrapper
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
                selectinload(Inventory.items),
                contains_eager(Inventory.product),
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

    async def find_by_product(
        self,
        product_id: UUID,
        warehouse_id: UUID | None = None,
    ) -> Inventory | None:
        """Get inventory record for a product, optionally filtered by warehouse."""
        stmt = (
            select(Inventory)
            .where(Inventory.product_id == product_id)
            .options(selectinload(Inventory.items))
        )

        if warehouse_id:
            stmt = stmt.where(Inventory.warehouse_id == warehouse_id)

        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def find_by_products(
        self,
        product_ids: list[UUID],
        warehouse_id: UUID,
    ) -> list[Inventory]:
        """Get inventory records for multiple products in a warehouse."""
        stmt = (
            select(Inventory)
            .where(Inventory.product_id.in_(product_ids))
            .where(Inventory.warehouse_id == warehouse_id)
            .options(selectinload(Inventory.items))
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
                selectinload(Inventory.items),
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
