from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.commission import (
    Credit,
    CreditBalance,
    CreditDetail,
    CreditSplitRate,
    Order,
)
from commons.db.v6.commission.credits.enums import CreditStatus
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Select, func, or_, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.credits.processors.update_order_on_credit_processor import (
    UpdateOrderOnCreditProcessor,
)
from app.graphql.credits.processors.validate_credit_split_rate_processor import (
    ValidateCreditSplitRateProcessor,
)
from app.graphql.credits.processors.validate_credit_status_processor import (
    ValidateCreditStatusProcessor,
)
from app.graphql.credits.repositories.credit_balance_repository import (
    CreditBalanceRepository,
)
from app.graphql.credits.strawberry.credit_landing_page_response import (
    CreditLandingPageResponse,
)


class CreditsRepository(BaseRepository[Credit]):
    landing_model = CreditLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.CREDIT

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: CreditBalanceRepository,
        processor_executor: ProcessorExecutor,
        validate_status_processor: ValidateCreditStatusProcessor,
        validate_split_rate_processor: ValidateCreditSplitRateProcessor,
        update_order_processor: UpdateOrderOnCreditProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Credit,
            processor_executor=processor_executor,
            processor_executor_classes=[
                validate_status_processor,
                validate_split_rate_processor,
                update_order_processor,
            ],
        )
        self.balance_repository = balance_repository

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Credit.id,
                Credit.created_at,
                User.full_name.label("created_by"),
                Credit.credit_number,
                Credit.status,
                Credit.credit_type,
                Credit.entity_date,
                CreditBalance.total.label("total"),
                Credit.locked,
                Credit.reason,
                Order.id.label("order_id"),
                Order.order_number,
                array([Credit.created_by_id]).label("user_ids"),
            )
            .select_from(Credit)
            .options(lazyload("*"))
            .join(User, User.id == Credit.created_by_id)
            .join(Order, Order.id == Credit.order_id)
            .join(CreditBalance, CreditBalance.id == Credit.balance_id)
        )

    async def find_credit_by_id(self, credit_id: UUID) -> Credit:
        credit = await self.get_by_id(
            credit_id,
            options=[
                joinedload(Credit.details),
                joinedload(Credit.details).joinedload(CreditDetail.outside_split_rates),
                joinedload(Credit.details)
                .joinedload(CreditDetail.outside_split_rates)
                .joinedload(CreditSplitRate.user),
                joinedload(Credit.balance),
                joinedload(Credit.order),
                joinedload(Credit.created_by),
                lazyload("*"),
            ],
        )
        if not credit:
            raise NotFoundError(str(credit_id))
        return credit

    async def create_with_balance(self, credit: Credit) -> Credit:
        balance = await self.balance_repository.create_from_details(credit.details)
        credit.balance_id = balance.id
        _ = await self.create(credit)
        return await self.find_credit_by_id(credit.id)

    async def update_with_balance(self, credit: Credit) -> Credit:
        updated = await self.update(credit)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.flush()
        return await self.find_credit_by_id(updated.id)

    async def credit_number_exists(self, order_id: UUID, credit_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Credit)
            .options(lazyload("*"))
            .where(
                Credit.order_id == order_id,
                Credit.credit_number == credit_number,
            )
        )
        return result.scalar_one() > 0

    async def find_by_credit_number(
        self, order_id: UUID, credit_number: str
    ) -> Credit | None:
        stmt = (
            select(Credit)
            .options(lazyload("*"))
            .where(
                Credit.order_id == order_id,
                Credit.credit_number == credit_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_credit_number(
        self,
        search_term: str,
        limit: int = 20,
        *,
        open_only: bool = False,
        unlocked_only: bool = False,
    ) -> list[Credit]:
        stmt = (
            select(Credit)
            .options(lazyload("*"))
            .where(Credit.credit_number.ilike(f"%{search_term}%"))
        )
        if open_only:
            stmt = stmt.where(Credit.status == CreditStatus.PENDING)
        if unlocked_only:
            stmt = stmt.where(Credit.locked.is_(False))
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Credit]:
        stmt = (
            select(Credit)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.INVOICE)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Credit.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.INVOICE)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Credit.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_order_id(self, order_id: UUID) -> list[Credit]:
        stmt = select(Credit).options(lazyload("*")).where(Credit.order_id == order_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
