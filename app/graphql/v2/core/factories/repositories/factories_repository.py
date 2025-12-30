from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.core.factories.factory_split_rate import FactorySplitRate
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.manufacturer_order_model import ManufacturerOrder
from sqlalchemy import Select, String, delete, func, literal, select
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.factories.processors.validate_factory_split_rates_processor import (
    ValidateFactorySplitRatesProcessor,
)
from app.graphql.v2.core.factories.strawberry.factory_landing_page_response import (
    FactoryLandingPageResponse,
)


class FactoriesRepository(BaseRepository[Factory]):
    entity_type = EntityType.FACTORY
    landing_model = FactoryLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.FACTORY

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        processor_executor: ProcessorExecutor,
        validate_factory_split_rates_processor: ValidateFactorySplitRatesProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Factory,
            processor_executor=processor_executor,
            processor_executor_classes=[validate_factory_split_rates_processor],
        )

    def paginated_stmt(self) -> Select[Any]:
        split_rate_user = aliased(User)
        empty_array = literal([]).cast(ARRAY(String))

        split_rates_subq = (
            select(
                FactorySplitRate.factory_id,
                func.coalesce(
                    func.array_agg(split_rate_user.full_name), empty_array
                ).label("split_rates"),
            )
            .join(split_rate_user, split_rate_user.id == FactorySplitRate.user_id)
            .group_by(FactorySplitRate.factory_id)
            .subquery()
        )

        return (
            select(
                Factory.id,
                Factory.created_at,
                User.full_name.label("created_by"),
                Factory.title,
                Factory.published,
                Factory.freight_discount_type,
                Factory.account_number,
                Factory.email,
                Factory.phone,
                Factory.lead_time,
                Factory.payment_terms,
                Factory.base_commission_rate,
                Factory.commission_discount_rate,
                Factory.overall_discount_rate,
                func.coalesce(split_rates_subq.c.split_rates, empty_array).label(
                    "split_rates"
                ),
                array([Factory.created_by_id]).label("user_ids"),
            )
            .select_from(Factory)
            .options(lazyload("*"))
            .join(User, User.id == Factory.created_by_id)
            .outerjoin(split_rates_subq, split_rates_subq.c.factory_id == Factory.id)
        )

    async def search_by_title(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Factory]:
        """
        Search factories by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)

        Returns:
            List of Factory objects matching the search criteria
        """
        stmt = (
            select(Factory)
            .options(
                joinedload(Factory.split_rates),
                joinedload(Factory.split_rates).joinedload(FactorySplitRate.user),
                joinedload(Factory.created_by),
                lazyload("*"),
            )
            .where(Factory.title.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if published is not None:
            stmt = stmt.where(Factory.published == published)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_manufacturer_order(self) -> dict[UUID, int]:
        """
        Get the current manufacturer order.

        Returns:
            Dictionary mapping factory_id to sort_order
        """
        stmt = select(ManufacturerOrder)
        result = await self.session.execute(stmt)
        orders = result.scalars().all()
        return {order.factory_id: order.sort_order for order in orders}

    async def update_manufacturer_order(self, factory_ids: list[UUID]) -> int:
        """
        Update the manufacturer order.

        Args:
            factory_ids: List of factory IDs in the desired order

        Returns:
            Number of manufacturers updated
        """
        # Delete all existing orders
        _ = await self.session.execute(delete(ManufacturerOrder))

        # Insert new orders
        for index, factory_id in enumerate(factory_ids):
            order = ManufacturerOrder(factory_id=factory_id, sort_order=index)
            self.session.add(order)

        await self.session.commit()
        return len(factory_ids)

    async def search_by_title_ordered(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Factory]:
        """
        Search factories by title with custom sort order applied.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)

        Returns:
            List of Factory objects sorted by custom order, then by title
        """
        # Get factories
        factories = await self.search_by_title(search_term, published, limit)

        # Get the order mapping
        order_map = await self.get_manufacturer_order()

        # Sort: factories with order first (by sort_order), then unordered (by title)
        def sort_key(factory: Factory) -> tuple[int, int, str]:
            if factory.id in order_map:
                return (0, order_map[factory.id], factory.title)
            return (1, 0, factory.title)

        return sorted(factories, key=sort_key)
