from uuid import UUID

from commons.db.v6.core.products.product_quantity_pricing import ProductQuantityPricing
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ProductQuantityPricingRepository(BaseRepository[ProductQuantityPricing]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, ProductQuantityPricing)

    async def list_by_product_id(
        self, product_id: UUID
    ) -> list[ProductQuantityPricing]:
        stmt = (
            select(ProductQuantityPricing)
            .where(ProductQuantityPricing.product_id == product_id)
            .options(joinedload(ProductQuantityPricing.product))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
