from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.factories import Factory
from commons.db.v6.core.products import Product, ProductCpn, ProductQuantityPricing
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class OverageRepository:
    def __init__(self, session: AsyncSession) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.session = session

    async def get_product(self, product_id: UUID) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_factory(self, factory_id: UUID) -> Factory | None:
        result = await self.session.execute(
            select(Factory).where(Factory.id == factory_id)
        )
        return result.scalar_one_or_none()

    async def get_customer_pricing(
        self, product_id: UUID, customer_id: UUID
    ) -> ProductCpn | None:
        result = await self.session.execute(
            select(ProductCpn)
            .where(ProductCpn.product_id == product_id)
            .where(ProductCpn.customer_id == customer_id)
        )
        return result.scalar_one_or_none()

    async def get_quantity_pricing(
        self, product_id: UUID, quantity: float
    ) -> ProductQuantityPricing | None:
        result = await self.session.execute(
            select(ProductQuantityPricing)
            .where(ProductQuantityPricing.product_id == product_id)
            .where(ProductQuantityPricing.quantity_low <= Decimal(str(quantity)))
            .where(ProductQuantityPricing.quantity_high >= Decimal(str(quantity)))
            .order_by(ProductQuantityPricing.quantity_low.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
