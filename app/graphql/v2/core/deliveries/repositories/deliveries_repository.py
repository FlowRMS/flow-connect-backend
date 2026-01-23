from typing import Any
from uuid import UUID

from commons.db.v6 import Delivery, DeliveryDocument, DeliveryItem
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class DeliveriesRepository(BaseRepository[Delivery]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, Delivery)

    @property
    def base_query(self) -> Select[Any]:
        """Base query with all relations loaded efficiently.

        Uses selectinload for collections to avoid cartesian products.
        Uses joinedload for single/scalar relationships.
        """
        return select(Delivery).options(
            # Collections - use selectinload
            selectinload(Delivery.items).options(
                joinedload(DeliveryItem.product),
                selectinload(DeliveryItem.receipts),
                selectinload(DeliveryItem.issues),
            ),
            selectinload(Delivery.status_history),
            selectinload(Delivery.issues),
            selectinload(Delivery.assignees),
            selectinload(Delivery.documents).selectinload(DeliveryDocument.file),
            # Single relationships - use joinedload
            joinedload(Delivery.recurring_shipment),
            joinedload(Delivery.vendor),
            joinedload(Delivery.carrier),
        )

    @property
    def list_query(self) -> Select[Any]:
        """Lite query for list endpoints (no eager relations)."""
        return select(Delivery)

    async def get_with_relations(self, delivery_id: UUID) -> Delivery | None:
        stmt = self.base_query.where(Delivery.id == delivery_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_by_warehouse_lite(
        self,
        warehouse_id: UUID,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Delivery]:
        stmt = self.list_query.where(Delivery.warehouse_id == warehouse_id)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all_lite(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Delivery]:
        stmt = self.list_query
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_warehouse(
        self,
        warehouse_id: UUID,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Delivery]:
        return await self.list_by_warehouse_lite(
            warehouse_id, limit=limit, offset=offset
        )

    async def list_all(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Delivery]:
        return await self.list_all_lite(limit=limit, offset=offset)
