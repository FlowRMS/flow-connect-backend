from uuid import UUID

from commons.db.v6 import DeliveryItemReceipt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class DeliveryItemReceiptsRepository(BaseRepository[DeliveryItemReceipt]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, DeliveryItemReceipt)

    async def list_by_delivery_item(
        self, delivery_item_id: UUID
    ) -> list[DeliveryItemReceipt]:
        stmt = select(DeliveryItemReceipt).where(
            DeliveryItemReceipt.delivery_item_id == delivery_item_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
