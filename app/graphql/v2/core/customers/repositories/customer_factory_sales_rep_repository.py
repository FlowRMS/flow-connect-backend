from uuid import UUID

from commons.db.v6.core.customers.customer_factory_sales_rep import (
    CustomerFactorySalesRep,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class CustomerFactorySalesRepRepository(BaseRepository[CustomerFactorySalesRep]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, CustomerFactorySalesRep)

    async def list_by_customer_and_factory(
        self,
        customer_id: UUID,
        factory_id: UUID,
    ) -> list[CustomerFactorySalesRep]:
        stmt = (
            select(CustomerFactorySalesRep)
            .where(
                CustomerFactorySalesRep.customer_id == customer_id,
                CustomerFactorySalesRep.factory_id == factory_id,
            )
            .options(
                joinedload(CustomerFactorySalesRep.customer),
                joinedload(CustomerFactorySalesRep.factory),
                joinedload(CustomerFactorySalesRep.user),
            )
            .order_by(CustomerFactorySalesRep.position)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_by_id_with_relations(
        self,
        rep_id: UUID,
    ) -> CustomerFactorySalesRep | None:
        stmt = (
            select(CustomerFactorySalesRep)
            .where(CustomerFactorySalesRep.id == rep_id)
            .options(
                joinedload(CustomerFactorySalesRep.customer),
                joinedload(CustomerFactorySalesRep.factory),
                joinedload(CustomerFactorySalesRep.user),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
