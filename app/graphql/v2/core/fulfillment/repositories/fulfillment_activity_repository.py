from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from commons.db.v6.fulfillment import FulfillmentActivity

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FulfillmentActivityRepository(BaseRepository[FulfillmentActivity]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, FulfillmentActivity)

    async def list_by_fulfillment_order(
        self, fulfillment_order_id: UUID
    ) -> list[FulfillmentActivity]:
        stmt = (
            select(FulfillmentActivity)
            .options(selectinload(FulfillmentActivity.created_by))
            .where(FulfillmentActivity.fulfillment_order_id == fulfillment_order_id)
            .order_by(FulfillmentActivity.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
