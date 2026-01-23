from uuid import UUID

from commons.db.v6 import DeliveryAssignee
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class DeliveryAssigneesRepository(BaseRepository[DeliveryAssignee]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, DeliveryAssignee)

    async def list_by_delivery(self, delivery_id: UUID) -> list[DeliveryAssignee]:
        stmt = select(DeliveryAssignee).where(
            DeliveryAssignee.delivery_id == delivery_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
