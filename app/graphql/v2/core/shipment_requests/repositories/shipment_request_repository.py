from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from commons.db.v6.crm.shipment_requests.shipment_request import (
    ShipmentRequest,
)


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
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ShipmentRequest]:
        stmt = (
            select(ShipmentRequest)
            .where(ShipmentRequest.warehouse_id == warehouse_id)
            .options(selectinload(ShipmentRequest.items))
            .limit(limit)
            .offset(offset)
        )

        if status:
            stmt = stmt.where(ShipmentRequest.status == status)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
