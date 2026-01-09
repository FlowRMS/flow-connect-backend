from uuid import UUID

from commons.db.v6.fulfillment import FulfillmentAssignment, FulfillmentAssignmentRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FulfillmentAssignmentRepository(BaseRepository[FulfillmentAssignment]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, FulfillmentAssignment)

    async def get_by_order_and_user(
        self, fulfillment_order_id: UUID, user_id: UUID
    ) -> FulfillmentAssignment | None:
        stmt = select(FulfillmentAssignment).where(
            FulfillmentAssignment.fulfillment_order_id == fulfillment_order_id,
            FulfillmentAssignment.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_fulfillment_order(
        self, fulfillment_order_id: UUID
    ) -> list[FulfillmentAssignment]:
        stmt = (
            select(FulfillmentAssignment)
            .options(selectinload(FulfillmentAssignment.user))
            .where(FulfillmentAssignment.fulfillment_order_id == fulfillment_order_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_role(
        self,
        fulfillment_order_id: UUID,
        role: FulfillmentAssignmentRole,
    ) -> list[FulfillmentAssignment]:
        stmt = (
            select(FulfillmentAssignment)
            .options(selectinload(FulfillmentAssignment.user))
            .where(
                FulfillmentAssignment.fulfillment_order_id == fulfillment_order_id,
                FulfillmentAssignment.role == role,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
