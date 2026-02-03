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
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import OutsideRepsRequiredError
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
            logger.debug(
                f"Applying default rep splits for order detail {detail.id} "
                f"of order {order.id}"
            )
            await self._apply_default_inside_reps(detail, factory_id)
            await self._apply_default_outside_reps(
                detail, sold_to_customer_id, factory_id
            )

        # now check if it is still empty and log, error if needed
        for detail in order.details:
            if not detail.inside_split_rates:
                logger.error(
                    f"Inside split rates are still empty for order detail {detail.id} "
                    f"after applying defaults."
                )

            if not detail.outside_split_rates:
                raise OutsideRepsRequiredError(
                    f"Outside split rates are required for order detail # {detail.item_number} "
                    f"but none were found after applying defaults."
                )

    async def _apply_default_inside_reps(
        self,
        detail: OrderDetail,
        factory_id: UUID,
    ) -> None:
        if detail.inside_split_rates:
            logger.debug(
                f"Inside reps already set for order detail {detail.id}, skipping default assignment."
            )
            return

        factory_split_rates = await self._get_factory_split_rates(factory_id)
        logger.debug(
            f"Assigning default inside reps from factory {factory_id} "
            f"to order detail {detail.id}: {factory_split_rates}"
        )
        inside_reps = []
        for sr in factory_split_rates:
            obj = OrderInsideRep(
                user_id=sr.user_id,
                split_rate=sr.split_rate,
                position=sr.position,
            )
            inside_reps.append(obj)
        detail.inside_split_rates = inside_reps

    async def _apply_default_outside_reps(
        self,
        detail: OrderDetail,
        customer_id: UUID,
        factory_id: UUID,
    ) -> None:
        if detail.outside_split_rates:
            logger.debug(
                f"Outside reps already set for order detail {detail.id}, skipping default assignment."
            )
            return

        customer_factory_reps = await self._get_customer_factory_split_rates(
            customer_id, factory_id
        )
        if customer_factory_reps:
            outside_reps = []
            for rep in customer_factory_reps:
                obj = OrderSplitRate(
                    user_id=rep.user_id,
                    split_rate=rep.rate,
                    position=rep.position,
                )
                outside_reps.append(obj)
            detail.outside_split_rates = outside_reps
            return

        customer_outside_reps = await self._get_customer_outside_reps(customer_id)
        outside_reps = []
        for rep in customer_outside_reps:
            obj = OrderSplitRate(
                user_id=rep.user_id,
                split_rate=rep.split_rate,
                position=rep.position,
            )
            outside_reps.append(obj)
        detail.outside_split_rates = outside_reps

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
