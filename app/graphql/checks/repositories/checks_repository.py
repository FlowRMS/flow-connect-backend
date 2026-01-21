from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.commission import (
    Adjustment,
    Check,
    CheckDetail,
    Credit,
    CreditDetail,
    Invoice,
    InvoiceDetail,
    InvoiceSplitRate,
    Order,
)
from commons.db.v6.core import Factory
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.checks.processors.validate_check_entities_processor import (
    ValidateCheckEntitiesProcessor,
)
from app.graphql.checks.strawberry.check_landing_page_response import (
    CheckLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy
from app.graphql.v2.rbac.strategies.created_by_filter import CreatedByFilterStrategy


class ChecksRepository(BaseRepository[Check]):
    entity_type = EntityType.CHECK
    landing_model = CheckLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.CHECK

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        processor_executor: ProcessorExecutor,
        validate_entities_processor: ValidateCheckEntitiesProcessor,
        rbac_filter_service: RbacFilterService,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Check,
            rbac_filter_service,
            processor_executor=processor_executor,
            processor_executor_classes=[
                validate_entities_processor,
            ],
        )

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return CreatedByFilterStrategy(RbacResourceEnum.CHECK, Check)

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Check.id,
                Check.entity_date.label("check_date"),
                Check.created_at,
                User.full_name.label("created_by"),
                Check.check_number,
                Check.status,
                Check.post_date,
                Check.entered_commission_amount,
                Check.commission_month,
                Factory.title.label("factory_name"),
                Check.user_ids,
            )
            .select_from(Check)
            .options(lazyload("*"))
            .join(User, User.id == Check.created_by_id)
            .join(Factory, Factory.id == Check.factory_id)
        )

    async def find_check_by_id(self, check_id: UUID) -> Check:
        check = await self.get_by_id(
            check_id,
            options=[
                joinedload(Check.created_by),
                joinedload(Check.details),
                joinedload(Check.details).joinedload(CheckDetail.invoice),
                joinedload(Check.details)
                .joinedload(CheckDetail.invoice)
                .joinedload(Invoice.balance),
                joinedload(Check.details)
                .joinedload(CheckDetail.invoice)
                .joinedload(Invoice.order),
                joinedload(Check.details)
                .joinedload(CheckDetail.invoice)
                .joinedload(Invoice.order)
                .joinedload(Order.sold_to_customer),
                joinedload(Check.details)
                .joinedload(CheckDetail.invoice)
                .joinedload(Invoice.order)
                .joinedload(Order.bill_to_customer),
                joinedload(Check.details)
                .joinedload(CheckDetail.invoice)
                .joinedload(Invoice.details),
                joinedload(Check.details)
                .joinedload(CheckDetail.invoice)
                .joinedload(Invoice.details)
                .joinedload(InvoiceDetail.outside_split_rates),
                joinedload(Check.details)
                .joinedload(CheckDetail.invoice)
                .joinedload(Invoice.details)
                .joinedload(InvoiceDetail.outside_split_rates)
                .joinedload(InvoiceSplitRate.user),
                joinedload(Check.details).joinedload(CheckDetail.credit),
                joinedload(Check.details)
                .joinedload(CheckDetail.credit)
                .joinedload(Credit.order),
                joinedload(Check.details).joinedload(CheckDetail.adjustment),
                joinedload(Check.details)
                .joinedload(CheckDetail.adjustment)
                .joinedload(Adjustment.customer),
                joinedload(Check.details)
                .joinedload(CheckDetail.adjustment)
                .joinedload(Adjustment.factory),
                joinedload(Check.factory),
                joinedload(Check.details)
                .joinedload(CheckDetail.credit)
                .joinedload(Credit.details),
                joinedload(Check.details)
                .joinedload(CheckDetail.credit)
                .joinedload(Credit.details)
                .joinedload(CreditDetail.outside_split_rates),
                joinedload(Check.details)
                .joinedload(CheckDetail.credit)
                .joinedload(Credit.balance),
                lazyload("*"),
            ],
        )
        if not check:
            raise NotFoundError(str(check_id))
        return check

    async def check_number_exists(self, factory_id: UUID, check_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Check)
            .options(lazyload("*"))
            .where(
                Check.factory_id == factory_id,
                Check.check_number == check_number,
            )
        )
        return result.scalar_one() > 0

    async def search_by_check_number(
        self, search_term: str, limit: int = 20
    ) -> list[Check]:
        stmt = (
            select(Check)
            .options(lazyload("*"))
            .where(Check.check_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_factory_id(self, factory_id: UUID) -> list[Check]:
        stmt = (
            select(Check).options(lazyload("*")).where(Check.factory_id == factory_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Check]:
        stmt = (
            select(Check)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.CHECK)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Check.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.CHECK)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Check.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_sold_to_customer_id(self, customer_id: UUID) -> list[Check]:
        stmt = (
            select(Check)
            .options(lazyload("*"))
            .join(CheckDetail, CheckDetail.check_id == Check.id)
            .join(Invoice, Invoice.id == CheckDetail.invoice_id)
            .join(Order, Order.id == Invoice.order_id)
            .where(Order.sold_to_customer_id == customer_id)
            .distinct()
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
