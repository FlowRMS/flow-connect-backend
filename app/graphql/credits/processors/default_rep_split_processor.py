from uuid import UUID

from commons.db.v6.commission import Credit, CreditSplitRate
from commons.db.v6.commission.orders import OrderDetail, OrderSplitRate
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class CreditDefaultRepSplitProcessor(BaseProcessor[Credit]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Credit]) -> None:
        credit = context.entity
        order_detail_ids = self._collect_order_detail_ids(credit)

        if not order_detail_ids:
            return

        order_details_map = await self._load_order_details(order_detail_ids)
        self._apply_outside_reps_from_order_details(credit, order_details_map)

    def _collect_order_detail_ids(self, credit: Credit) -> list[UUID]:
        return [
            detail.order_detail_id
            for detail in credit.details
            if detail.order_detail_id and not detail.outside_split_rates
        ]

    async def _load_order_details(
        self, order_detail_ids: list[UUID]
    ) -> dict[UUID, OrderDetail]:
        stmt = (
            select(OrderDetail)
            .options(joinedload(OrderDetail.outside_split_rates))
            .where(OrderDetail.id.in_(order_detail_ids))
        )
        result = await self._session.execute(stmt)
        order_details = result.unique().scalars().all()
        return {od.id: od for od in order_details}

    def _apply_outside_reps_from_order_details(
        self,
        credit: Credit,
        order_details_map: dict[UUID, OrderDetail],
    ) -> None:
        for detail in credit.details:
            if detail.outside_split_rates or not detail.order_detail_id:
                continue

            order_detail = order_details_map.get(detail.order_detail_id)
            if not order_detail or not order_detail.outside_split_rates:
                continue

            detail.outside_split_rates = self._convert_split_rates(
                order_detail.outside_split_rates
            )
            logger.debug(
                f"Applied outside reps from order detail {order_detail.id} "
                f"to credit detail {detail.id}"
            )

    def _convert_split_rates(
        self, order_split_rates: list[OrderSplitRate]
    ) -> list[CreditSplitRate]:
        result = []
        for sr in order_split_rates:
            obj = CreditSplitRate(
                user_id=sr.user_id,
                split_rate=sr.split_rate,
                position=sr.position,
            )
            result.append(obj)
        return result
