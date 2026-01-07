from uuid import UUID

from commons.db.v6.warehouse.shipment_requests import (
    ShipmentRequest,
    ShipmentRequestStatus,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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

    async def find_by_warehouse(
        self,
        warehouse_id: UUID,
        status: ShipmentRequestStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ShipmentRequest]:
        stmt = (
            select(ShipmentRequest)
            .where(ShipmentRequest.warehouse_id == warehouse_id)
            .options(
                joinedload(ShipmentRequest.items),
                joinedload(ShipmentRequest.factory),
            )
            .limit(limit)
            .offset(offset)
        )

        if status:
            stmt = stmt.where(ShipmentRequest.status == status)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
