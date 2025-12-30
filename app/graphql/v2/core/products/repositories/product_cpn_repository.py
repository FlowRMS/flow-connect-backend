from uuid import UUID

from commons.db.v6.core.products.product_cpn import ProductCpn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ProductCpnRepository(BaseRepository[ProductCpn]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, ProductCpn)

    async def list_by_product_id(self, product_id: UUID) -> list[ProductCpn]:
        stmt = (
            select(ProductCpn)
            .where(ProductCpn.product_id == product_id)
            .options(
                joinedload(ProductCpn.customer),
                joinedload(ProductCpn.product),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_by_id_with_relations(self, cpn_id: UUID) -> ProductCpn | None:
        stmt = (
            select(ProductCpn)
            .where(ProductCpn.id == cpn_id)
            .options(
                joinedload(ProductCpn.customer),
                joinedload(ProductCpn.product),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_cpn_by_product_and_customer(
        self, product_id: UUID, customer_id: UUID
    ) -> ProductCpn | None:
        stmt = (
            select(ProductCpn)
            .where(
                ProductCpn.product_id == product_id,
                ProductCpn.customer_id == customer_id,
            )
            .options(lazyload("*"))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
