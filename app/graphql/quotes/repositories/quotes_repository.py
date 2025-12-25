from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.quotes import Quote, QuoteBalance
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.quotes.processors.validate_rep_split_processor import (
    ValidateRepSplitProcessor,
)
from app.graphql.quotes.repositories.quote_balance_repository import (
    QuoteBalanceRepository,
)
from app.graphql.quotes.strategies.quote_owner_filter import QuoteOwnerFilterStrategy
from app.graphql.quotes.strawberry.quote_landing_page_response import (
    QuoteLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class QuotesRepository(BaseRepository[Quote]):
    entity_type = EntityType.QUOTE
    rbac_resource = RbacResourceEnum.QUOTE
    landing_model = QuoteLandingPageResponse

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: QuoteBalanceRepository,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
        validate_rep_split_processor: ValidateRepSplitProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Quote,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[validate_rep_split_processor],
        )
        self.balance_repository = balance_repository

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return QuoteOwnerFilterStrategy(RbacResourceEnum.QUOTE)

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Quote.id,
                Quote.created_at,
                User.full_name.label("created_by"),
                Quote.quote_number,
                Quote.status,
                Quote.pipeline_stage,
                Quote.entity_date,
                Quote.exp_date,
                QuoteBalance.total.label("total"),
                Quote.published,
            )
            .select_from(Quote)
            .options(lazyload("*"))
            .join(User, User.id == Quote.created_by_id)
            .join(QuoteBalance, QuoteBalance.id == Quote.balance_id)
        )

    async def create_with_balance(self, quote: Quote) -> Quote:
        balance = await self.balance_repository.create_from_details(quote.details)
        quote.balance_id = balance.id
        return await self.create(quote)

    async def update_with_balance(self, quote: Quote) -> Quote:
        updated = await self.update(quote)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.refresh(updated)
        return updated

    async def quote_number_exists(self, quote_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Quote)
            .where(Quote.quote_number == quote_number)
        )
        return result.scalar_one() > 0

    async def search_by_quote_number(
        self, search_term: str, limit: int = 20
    ) -> list[Quote]:
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .where(Quote.quote_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Quote]:
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.QUOTE)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Quote.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.QUOTE)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Quote.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
