from typing import Any
from uuid import UUID

from commons.db.v6 import User
from commons.db.v6.commission import Adjustment, AdjustmentSplitRate
from commons.db.v6.rbac.rbac_resource_enum import RbacResourceEnum
from sqlalchemy import Select, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.adjustments.processors.validate_adjustment_status_processor import (
    ValidateAdjustmentStatusProcessor,
)
from app.graphql.adjustments.strawberry.adjustment_landing_page_response import (
    AdjustmentLandingPageResponse,
)
from app.graphql.base_repository import BaseRepository


class AdjustmentsRepository(BaseRepository[Adjustment]):
    landing_model = AdjustmentLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.ADJUSTMENT

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        processor_executor: ProcessorExecutor,
        validate_status_processor: ValidateAdjustmentStatusProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Adjustment,
            processor_executor=processor_executor,
            processor_executor_classes=[
                validate_status_processor,
            ],
        )

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Adjustment.id,
                Adjustment.created_at,
                User.full_name.label("created_by"),
                Adjustment.adjustment_number,
                Adjustment.status,
                Adjustment.entity_date,
                Adjustment.amount,
                Adjustment.locked,
                Adjustment.reason,
                array([Adjustment.created_by_id]).label("user_ids"),
            )
            .select_from(Adjustment)
            .options(lazyload("*"))
            .join(User, User.id == Adjustment.created_by_id)
        )

    async def find_adjustment_by_id(self, adjustment_id: UUID) -> Adjustment:
        adjustment = await self.get_by_id(
            adjustment_id,
            options=[
                joinedload(Adjustment.split_rates),
                joinedload(Adjustment.split_rates).joinedload(AdjustmentSplitRate.user),
                joinedload(Adjustment.factory),
                joinedload(Adjustment.customer),
                joinedload(Adjustment.created_by),
                lazyload("*"),
            ],
        )
        if not adjustment:
            raise NotFoundError(str(adjustment_id))
        return adjustment

    async def find_by_factory_id(self, factory_id: UUID) -> list[Adjustment]:
        stmt = (
            select(Adjustment)
            .options(lazyload("*"))
            .where(Adjustment.factory_id == factory_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_reason(
        self, search_term: str, limit: int = 20
    ) -> list[Adjustment]:
        stmt = (
            select(Adjustment)
            .options(lazyload("*"))
            .where(Adjustment.reason.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
