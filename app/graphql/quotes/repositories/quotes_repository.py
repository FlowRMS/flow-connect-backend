from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.quotes import (
    Quote,
    QuoteBalance,
    QuoteDetail,
)
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor, ValidateCommissionRateProcessor
from app.core.processors.events import RepositoryEvent
from app.graphql.base_repository import BaseRepository
from app.graphql.quotes.processors import (
    DefaultRepSplitProcessor,
    ValidateQuoteReferencesProcessor,
    ValidateRepSplitProcessor,
)
from app.graphql.quotes.repositories.quote_balance_repository import (
    QuoteBalanceRepository,
)
from app.graphql.quotes.repositories.quote_bulk_query_helper import (
    build_find_quote_by_number_with_details_stmt,
    build_find_quotes_by_quote_numbers_stmt,
)
from app.graphql.quotes.repositories.quote_landing_query_builder import (
    QuoteLandingQueryBuilder,
)
from app.graphql.quotes.strategies.quote_owner_filter import QuoteOwnerFilterStrategy
from app.graphql.quotes.strategies.sales_team_quote_filter import (
    SalesTeamQuoteFilterStrategy,
)
from app.graphql.quotes.strawberry.quote_landing_page_response import (
    QuoteLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy
from app.graphql.watchers.processors import QuoteWatcherNotificationProcessor


class QuotesRepository(BaseRepository[Quote]):
    entity_type = EntityType.QUOTE
    landing_model = QuoteLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.QUOTE

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: QuoteBalanceRepository,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
        default_rep_split_processor: DefaultRepSplitProcessor,
        validate_rep_split_processor: ValidateRepSplitProcessor,
        validate_commission_rate_processor: ValidateCommissionRateProcessor,
        validate_quote_references_processor: ValidateQuoteReferencesProcessor,
        quote_watcher_notification_processor: QuoteWatcherNotificationProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Quote,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[
                default_rep_split_processor,
                validate_rep_split_processor,
                validate_commission_rate_processor,
                validate_quote_references_processor,
                quote_watcher_notification_processor,
            ],
        )
        self.balance_repository = balance_repository

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        if RbacRoleEnum.SALES_MANAGER in self.auth_info.roles:
            return SalesTeamQuoteFilterStrategy(RbacResourceEnum.QUOTE)
        return QuoteOwnerFilterStrategy(RbacResourceEnum.QUOTE)

    def paginated_stmt(self) -> Select[Any]:
        return QuoteLandingQueryBuilder().build()

    @override
    def compute_user_ids(self, quote: Quote) -> list[UUID]:
        user_ids: set[UUID] = {self.auth_info.flow_user_id}
        for detail in quote.details:
            for split_rate in detail.outside_split_rates:
                user_ids.add(split_rate.user_id)
            for inside_rep in detail.inside_split_rates:
                user_ids.add(inside_rep.user_id)
        return list(user_ids)

    async def find_quote_by_id(self, quote_id: UUID) -> Quote:
        quote = await self.get_by_id(
            quote_id,
            options=[
                joinedload(Quote.details),
                joinedload(Quote.details).joinedload(QuoteDetail.product),
                joinedload(Quote.details).joinedload(QuoteDetail.outside_split_rates),
                joinedload(Quote.details).joinedload(QuoteDetail.inside_split_rates),
                joinedload(Quote.details).joinedload(QuoteDetail.uom),
                joinedload(Quote.details).joinedload(QuoteDetail.order),
                joinedload(Quote.details).joinedload(QuoteDetail.factory),
                joinedload(Quote.details).joinedload(QuoteDetail.end_user),
                joinedload(Quote.balance),
                joinedload(Quote.sold_to_customer),
                joinedload(Quote.bill_to_customer),
                joinedload(Quote.created_by),
                joinedload(Quote.job),
                lazyload("*"),
            ],
        )
        if not quote:
            raise NotFoundError(str(quote_id))
        return quote

    async def create_with_balance(self, quote: Quote) -> Quote:
        balance = await self.balance_repository.create_from_details(quote.details)
        quote.balance_id = balance.id
        _ = await self.create(quote)
        return await self.find_quote_by_id(quote.id)

    async def update_with_balance(self, quote: Quote) -> Quote:
        updated = await self.update(quote)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.flush()
        return await self.find_quote_by_id(updated.id)

    async def quote_number_exists(self, quote_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Quote)
            .where(Quote.quote_number == quote_number)
        )
        return result.scalar_one() > 0

    async def find_by_quote_number_with_details(
        self, quote_number: str
    ) -> Quote | None:
        stmt = build_find_quote_by_number_with_details_stmt(quote_number)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_quotes_by_quote_numbers(
        self, quote_numbers: list[str]
    ) -> list[Quote]:
        if not quote_numbers:
            return []
        stmt = build_find_quotes_by_quote_numbers_stmt(quote_numbers)
        result = await self.execute(stmt)
        rows = result.unique().scalars().all()
        by_number = {q.quote_number: q for q in rows}
        return [by_number[num] for num in quote_numbers if num in by_number]

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

    async def update_detail_order_ids(
        self, detail_ids: list[UUID], order_id: UUID
    ) -> None:
        stmt = (
            update(QuoteDetail)
            .where(QuoteDetail.id.in_(detail_ids))
            .values(order_id=order_id)
        )
        _ = await self.session.execute(stmt)

    async def get_existing_quotes(self, quote_numbers: list[str]) -> list[Quote]:
        if not quote_numbers:
            return []
        stmt = (
            select(Quote)
            .options(
                lazyload("*"),
            )
            .where(Quote.quote_number.in_(quote_numbers))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_sold_to_customer_id(self, customer_id: UUID) -> list[Quote]:
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .where(Quote.sold_to_customer_id == customer_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_balances_bulk(
        self,
        details_list: list[list[QuoteDetail]],
    ) -> list[QuoteBalance]:
        balances = [
            self.balance_repository.calculate_balance_from_details(details)
            for details in details_list
        ]
        self.session.add_all(balances)
        await self.session.flush(balances)
        return balances

    async def create_bulk(self, quotes: list[Quote]) -> list[Quote]:
        for quote in quotes:
            quote = await self.prepare_create(quote)

        self.session.add_all(quotes)
        await self.session.flush(quotes)

        for quote in quotes:
            await self._run_processors(RepositoryEvent.POST_CREATE, quote)

        return quotes
