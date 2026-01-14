from uuid import UUID

from commons.db.v6.warehouse.shipment_requests import (
    ShipmentRequest,
    ShipmentRequestItem,
    ShipmentRequestStatus,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET
from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ShipmentRequestRepository(BaseRepository[ShipmentRequest]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            ShipmentRequest,
        )

    def _default_options(self) -> list:
        return [
            joinedload(ShipmentRequest.items).joinedload(ShipmentRequestItem.product),
            joinedload(ShipmentRequest.factory),
        ]

    async def get_by_id(self, entity_id: UUID | str) -> ShipmentRequest | None:
        if isinstance(entity_id, str):
            entity_id = UUID(entity_id)
        stmt = (
            select(ShipmentRequest)
            .where(ShipmentRequest.id == entity_id)
            .options(*self._default_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_warehouse(
        self,
        warehouse_id: UUID,
        status: ShipmentRequestStatus | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[ShipmentRequest]:
        stmt = (
            select(ShipmentRequest)
            .where(ShipmentRequest.warehouse_id == warehouse_id)
            .options(
                joinedload(ShipmentRequest.items).joinedload(
                    ShipmentRequestItem.product
                ),
                joinedload(ShipmentRequest.factory),
            )
            .limit(limit)
            .offset(offset)
        )

        if status:
            stmt = stmt.where(ShipmentRequest.status == status)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def create(self, request: ShipmentRequest) -> ShipmentRequest:
        """Create a new shipment request with eager loading of relationships."""
        created = await super().create(request)

        # Refresh with eager loading to avoid lazy load errors
        await self.session.refresh(created, attribute_names=["items", "factory"])

        return created
