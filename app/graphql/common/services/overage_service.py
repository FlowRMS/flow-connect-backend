from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.factories import OverageTypeEnum as DbOverageTypeEnum
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.common.repositories.overage_repository import OverageRepository
from app.graphql.common.services.overage_pricing_calculator import (
    OveragePricingCalculator,
)
from app.graphql.common.strawberry.overage_record import (
    OverageRecord,
)
from app.graphql.common.strawberry.overage_record import (
    OverageTypeEnum as GqlOverageTypeEnum,
)


def _convert_overage_type(db_type: DbOverageTypeEnum) -> GqlOverageTypeEnum:
    if db_type == DbOverageTypeEnum.BY_TOTAL:
        return GqlOverageTypeEnum.BY_TOTAL
    return GqlOverageTypeEnum.BY_LINE


class OverageService:
    def __init__(self, session: AsyncSession) -> None:  # pyright: ignore[reportMissingSuperCall]
        self._repo = OverageRepository(session)
        self._calc = OveragePricingCalculator()

    async def find_effective_commission_rate_and_overage(
        self,
        product_id: UUID,
        detail_unit_price: float,
        factory_id: UUID,
        end_user_id: UUID,
        quantity: float = 1.0,
    ) -> OverageRecord:
        if detail_unit_price <= 0:
            raise ValueError(
                f"detail_unit_price must be positive, got: {detail_unit_price}"
            )

        product = await self._repo.get_product(product_id)
        if not product:
            return OverageRecord(
                success=False, error_message=f"Product with id {product_id} not found"
            )

        factory = await self._repo.get_factory(factory_id)
        if not factory:
            return OverageRecord(
                success=False, error_message=f"Factory with id {factory_id} not found"
            )

        customer_commission_rate: float | None = None
        customer_pricing = None
        if end_user_id:
            customer_pricing = await self._repo.get_customer_pricing(
                product_id, end_user_id
            )
            if customer_pricing and customer_pricing.commission_rate:
                customer_commission_rate = float(customer_pricing.commission_rate)

        if customer_pricing and customer_pricing.unit_price:
            base_unit_price = float(customer_pricing.unit_price)
        else:
            base_unit_price = float(product.unit_price) if product.unit_price else None

        gql_overage_type = _convert_overage_type(factory.overage_type)

        if not factory.overage_allowed:
            return OverageRecord(
                effective_commission_rate=self._calc.get_product_commission_rate(
                    product, factory, customer_commission_rate
                ),
                overage_unit_price=None,
                base_unit_price=base_unit_price,
                rep_share=None,
                level_rate=None,
                level_unit_price=None,
                overage_type=gql_overage_type,
            )

        if factory.overage_type == DbOverageTypeEnum.BY_TOTAL:
            return OverageRecord(
                success=False,
                error_message="BY_TOTAL overage must be calculated at the quote level. Use calculate_quote_overage_by_total() instead.",
                base_unit_price=base_unit_price,
                overage_type=gql_overage_type,
            )

        if base_unit_price and detail_unit_price <= base_unit_price:
            return OverageRecord(
                effective_commission_rate=self._calc.get_product_commission_rate(
                    product, factory, customer_commission_rate
                ),
                overage_unit_price=None,
                base_unit_price=base_unit_price,
                rep_share=None,
                level_rate=None,
                level_unit_price=None,
                overage_type=gql_overage_type,
            )

        overage_unit_price = self._calc.calculate_overage_unit_price(
            product, detail_unit_price
        )

        rep_share: float | None = None
        if factory.rep_overage_share:
            rep_share = float(factory.rep_overage_share) / 100.0

        level_rate, level_unit_price = await self._get_level_pricing(product, quantity)

        effective_commission_rate = self._calc.calculate_effective_commission_rate(
            product,
            factory,
            detail_unit_price,
            overage_unit_price,
            customer_commission_rate,
        )

        return OverageRecord(
            effective_commission_rate=effective_commission_rate,
            overage_unit_price=overage_unit_price,
            base_unit_price=base_unit_price,
            rep_share=rep_share,
            level_rate=level_rate,
            level_unit_price=level_unit_price,
            overage_type=gql_overage_type,
        )

    async def _get_level_pricing(
        self,
        product,
        quantity: float,
    ) -> tuple[float | None, float | None]:
        pricing = await self._repo.get_quantity_pricing(product.id, quantity)
        if not pricing:
            return None, None

        level_unit_price = float(pricing.unit_price) if pricing.unit_price else None
        base_unit_price = float(product.unit_price) if product.unit_price else None
        level_rate = self._calc.calculate_level_rate(level_unit_price, base_unit_price)

        return level_rate, level_unit_price

    async def calculate_quote_overage_by_total(
        self,
        factory_id: UUID,
        line_items: list[dict],
    ) -> OverageRecord:
        factory = await self._repo.get_factory(factory_id)
        if not factory:
            return OverageRecord(
                success=False, error_message=f"Factory with id {factory_id} not found"
            )

        gql_overage_type = _convert_overage_type(factory.overage_type)

        if not factory.overage_allowed:
            return OverageRecord(
                success=False,
                error_message="Overage is not allowed for this factory",
                overage_type=gql_overage_type,
            )

        if factory.overage_type != DbOverageTypeEnum.BY_TOTAL:
            return OverageRecord(
                success=False,
                error_message="Factory is configured for BY_LINE overage, not BY_TOTAL",
                overage_type=gql_overage_type,
            )

        total_base_amount = Decimal("0")
        total_sell_amount = Decimal("0")

        for item in line_items:
            product = await self._repo.get_product(item["product_id"])
            if not product:
                continue

            quantity = Decimal(str(item.get("quantity", 1)))
            detail_unit_price = Decimal(str(item["detail_unit_price"]))
            base_unit_price = product.unit_price or Decimal("0")

            total_base_amount += base_unit_price * quantity
            total_sell_amount += detail_unit_price * quantity

        overage_amount: float | None = None
        if total_sell_amount > total_base_amount:
            overage_amount = float(total_sell_amount - total_base_amount)

        rep_share = (
            float(factory.rep_overage_share) / 100.0
            if factory.rep_overage_share
            else 1.0
        )

        base_rate = (
            float(factory.base_commission_rate)
            if factory.base_commission_rate
            else None
        )

        effective_rate: float | None = None
        if base_rate and overage_amount and float(total_sell_amount) > 0:
            base_portion = float(total_base_amount) / float(total_sell_amount)
            overage_portion = overage_amount / float(total_sell_amount)
            effective_rate = (base_rate * base_portion) + (
                base_rate * rep_share * overage_portion
            )
        elif base_rate:
            effective_rate = base_rate

        return OverageRecord(
            effective_commission_rate=effective_rate,
            overage_unit_price=overage_amount,
            base_unit_price=float(total_base_amount),
            rep_share=rep_share,
            level_rate=None,
            level_unit_price=None,
            overage_type=gql_overage_type,
        )
