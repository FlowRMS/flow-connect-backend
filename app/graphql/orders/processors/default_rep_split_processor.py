from uuid import UUID

from commons.db.v6.commission.orders import (
    Order,
    OrderDetail,
    OrderInsideRep,
    OrderSplitRate,
)
from commons.db.v6.core.customers.customer_factory_sales_rep import (
    CustomerFactorySalesRep,
)
from commons.db.v6.core.customers.customer_split_rate import CustomerSplitRate
from commons.db.v6.core.factories.factory_split_rate import FactorySplitRate
from commons.db.v6.user.rep_type import RepTypeEnum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class OrderDefaultRepSplitProcessor(BaseProcessor[Order]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Order]) -> None:
        order = context.entity
        sold_to_customer_id = order.sold_to_customer_id
        factory_id = order.factory_id

        for detail in order.details:
            await self._apply_default_inside_reps(detail, factory_id)
            await self._apply_default_outside_reps(
                detail, sold_to_customer_id, factory_id
            )

    async def _apply_default_inside_reps(
        self,
        detail: OrderDetail,
        factory_id: UUID,
    ) -> None:
        if detail.inside_split_rates:
            return

        factory_split_rates = await self._get_factory_split_rates(factory_id)
        detail.inside_split_rates = [
            OrderInsideRep(
                user_id=sr.user_id,
                split_rate=sr.split_rate,
                position=sr.position,
            )
            for sr in factory_split_rates
        ]

    async def _apply_default_outside_reps(
        self,
        detail: OrderDetail,
        customer_id: UUID,
        factory_id: UUID,
    ) -> None:
        if detail.outside_split_rates:
            return

        customer_factory_reps = await self._get_customer_factory_split_rates(
            customer_id, factory_id
        )
        if customer_factory_reps:
            detail.outside_split_rates = [
                OrderSplitRate(
                    user_id=rep.user_id,
                    split_rate=rep.rate,
                    position=rep.position,
                )
                for rep in customer_factory_reps
            ]
            return

        customer_outside_reps = await self._get_customer_outside_reps(customer_id)
        detail.outside_split_rates = [
            OrderSplitRate(
                user_id=rep.user_id,
                split_rate=rep.split_rate,
                position=rep.position,
            )
            for rep in customer_outside_reps
        ]

    async def _get_factory_split_rates(
        self, factory_id: UUID
    ) -> list[FactorySplitRate]:
        stmt = (
            select(FactorySplitRate)
            .where(FactorySplitRate.factory_id == factory_id)
            .order_by(FactorySplitRate.position)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def _get_customer_factory_split_rates(
        self, customer_id: UUID, factory_id: UUID
    ) -> list[CustomerFactorySalesRep]:
        stmt = (
            select(CustomerFactorySalesRep)
            .where(
                CustomerFactorySalesRep.customer_id == customer_id,
                CustomerFactorySalesRep.factory_id == factory_id,
            )
            .order_by(CustomerFactorySalesRep.position)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def _get_customer_outside_reps(
        self, customer_id: UUID
    ) -> list[CustomerSplitRate]:
        stmt = (
            select(CustomerSplitRate)
            .where(
                CustomerSplitRate.customer_id == customer_id,
                CustomerSplitRate.rep_type == RepTypeEnum.OUTSIDE,
            )
            .order_by(CustomerSplitRate.position)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
