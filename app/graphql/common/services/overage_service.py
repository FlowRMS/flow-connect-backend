"""
Overage Service
Calculates overage pricing and effective commission rates

Supports two calculation modes (configured per factory):
- BY_LINE: Calculate overage on each line item individually
- BY_TOTAL: Calculate overage on the total quote/order amount (requires quote-level calculation)
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from commons.db.v6.core.factories import Factory
from commons.db.v6.core.factories import OverageTypeEnum as DbOverageTypeEnum
from commons.db.v6.core.products import Product, ProductCpn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.common.strawberry.overage_record import (
    OverageRecord,
)
from app.graphql.common.strawberry.overage_record import (
    OverageTypeEnum as GqlOverageTypeEnum,
)


def _convert_overage_type(db_type: DbOverageTypeEnum) -> GqlOverageTypeEnum:
    """Convert database OverageTypeEnum to GraphQL OverageTypeEnum."""
    if db_type == DbOverageTypeEnum.BY_TOTAL:
        return GqlOverageTypeEnum.BY_TOTAL
    return GqlOverageTypeEnum.BY_LINE


class OverageService:
    """
    Service for calculating overage pricing and commission rates.

    Overage occurs when a product is sold above its base price. The factory
    configuration determines:
    - Whether overage is allowed (overage_allowed)
    - How overage is calculated (overage_type: BY_LINE or BY_TOTAL)
    - What percentage of overage goes to the rep (rep_overage_share)
    """

    def __init__(self, session: AsyncSession):  # pyright: ignore[reportMissingSuperCall]
        self.session = session

    async def find_effective_commission_rate_and_overage(
        self,
        product_id: UUID,
        detail_unit_price: float,
        factory_id: UUID,
        end_user_id: UUID,
        quantity: float = 1.0,
    ) -> OverageRecord:
        """
        Calculate effective commission rate and overage unit price for a product.

        Args:
            product_id: The product UUID
            detail_unit_price: The unit price from the quote/order detail
            factory_id: The factory/manufacturer UUID
            end_user_id: The end user customer UUID (reserved for future end-user-specific pricing)
            quantity: The quantity being purchased (used for quantity-based pricing levels)

        Returns:
            OverageRecord with calculated values

        Raises:
            ValueError: If detail_unit_price is zero or negative
        """
        # Validate input to prevent division by zero
        if detail_unit_price <= 0:
            raise ValueError(
                f"detail_unit_price must be positive, got: {detail_unit_price}"
            )

        # Fetch product with overage settings
        product = await self._get_product(product_id)
        if not product:
            return OverageRecord(
                success=False, error_message=f"Product with id {product_id} not found"
            )

        # Fetch factory with overage settings
        factory = await self._get_factory(factory_id)
        if not factory:
            return OverageRecord(
                success=False, error_message=f"Factory with id {factory_id} not found"
            )

        # Check for customer-specific pricing (ProductCpn)
        customer_pricing: ProductCpn | None = None
        customer_commission_rate: float | None = None
        if end_user_id:
            customer_pricing = await self._get_customer_pricing(product_id, end_user_id)
            if customer_pricing and customer_pricing.commission_rate:
                customer_commission_rate = float(customer_pricing.commission_rate)

        # Get base values - use customer-specific price if available, otherwise product.unit_price
        if customer_pricing and customer_pricing.unit_price:
            base_unit_price = float(customer_pricing.unit_price)
        else:
            base_unit_price = float(product.unit_price) if product.unit_price else None

        # Get the overage type for responses
        gql_overage_type = _convert_overage_type(factory.overage_type)

        # Check if overage is allowed for this factory
        if not factory.overage_allowed:
            # Overage not enabled - return basic commission info
            return OverageRecord(
                effective_commission_rate=self._get_product_commission_rate(
                    product, factory, customer_commission_rate
                ),
                overage_unit_price=None,
                base_unit_price=base_unit_price,
                rep_share=None,
                level_rate=None,
                level_unit_price=None,
                overage_type=gql_overage_type,
            )

        # Check if this is a BY_TOTAL calculation - that requires quote-level processing
        if factory.overage_type == DbOverageTypeEnum.BY_TOTAL:
            # BY_TOTAL overage must be calculated at the quote/order level
            # This method handles BY_LINE only - return error for BY_TOTAL
            return OverageRecord(
                success=False,
                error_message="BY_TOTAL overage must be calculated at the quote level. Use calculate_quote_overage_by_total() instead.",
                base_unit_price=base_unit_price,
                overage_type=gql_overage_type,
            )

        # BY_LINE calculation: Check if there's overage on this line
        if base_unit_price and detail_unit_price <= base_unit_price:
            # No overage - detail price is at or below base price
            return OverageRecord(
                effective_commission_rate=self._get_product_commission_rate(
                    product, factory, customer_commission_rate
                ),
                overage_unit_price=None,
                base_unit_price=base_unit_price,
                rep_share=None,
                level_rate=None,
                level_unit_price=None,
                overage_type=gql_overage_type,
            )

        # Calculate overage for BY_LINE mode
        overage_unit_price = self._calculate_overage_unit_price(
            product, detail_unit_price
        )

        # Get rep's share of overage from factory settings (as percentage, e.g., 100.00 = 100%)
        rep_share: float | None = None
        if factory.rep_overage_share:
            rep_share = (
                float(factory.rep_overage_share) / 100.0
            )  # Convert to decimal (100% -> 1.0)

        # Get level rate and price (from product quantity-based pricing if available)
        level_rate, level_unit_price = await self._get_level_pricing(product, quantity)

        # Calculate effective commission rate
        effective_commission_rate = self._calculate_effective_commission_rate(
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

    async def _get_product(self, product_id: UUID) -> Optional[Product]:
        """Fetch product by ID"""
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def _get_factory(self, factory_id: UUID) -> Optional[Factory]:
        """Fetch factory by ID"""
        result = await self.session.execute(
            select(Factory).where(Factory.id == factory_id)
        )
        return result.scalar_one_or_none()

    async def _get_customer_pricing(
        self, product_id: UUID, customer_id: UUID
    ) -> Optional[ProductCpn]:
        """
        Fetch customer-specific pricing (CPN) for a product.

        ProductCpn contains customer-specific:
        - unit_price: Custom price for this customer
        - commission_rate: Custom commission rate for this customer
        - customer_part_number: Customer's internal part number

        Args:
            product_id: The product UUID
            customer_id: The end user (customer) UUID

        Returns:
            ProductCpn if customer-specific pricing exists, None otherwise
        """
        result = await self.session.execute(
            select(ProductCpn)
            .where(ProductCpn.product_id == product_id)
            .where(ProductCpn.customer_id == customer_id)
        )
        return result.scalar_one_or_none()

    def _get_product_commission_rate(
        self,
        product: Product,
        factory: Factory | None = None,
        customer_rate_override: float | None = None,
    ) -> Optional[float]:
        """
        Get the base commission rate with priority:
        1. Customer-specific rate (from ProductCpn) if provided
        2. Product default_commission_rate
        3. Factory base_commission_rate

        Args:
            product: The product
            factory: The factory (optional, for fallback rate)
            customer_rate_override: Customer-specific commission rate from ProductCpn
        """
        # 1. Customer-specific rate takes priority
        if customer_rate_override is not None:
            return customer_rate_override

        # 2. Product has default_commission_rate
        if product.default_commission_rate:
            return float(product.default_commission_rate)

        # 3. Fall back to factory's base_commission_rate
        if factory and factory.base_commission_rate:
            return float(factory.base_commission_rate)

        return None

    def _calculate_overage_unit_price(
        self,
        product: Product,
        detail_unit_price: float,
    ) -> Optional[float]:
        """
        Calculate overage unit price.
        Overage = detail_unit_price - base_price (if detail > base)

        Uses product.unit_price as the base price.
        """
        # Use unit_price as base price (list_price doesn't exist in model)
        base_price = float(product.unit_price) if product.unit_price else 0

        if detail_unit_price > base_price:
            return detail_unit_price - base_price

        return None

    async def _get_level_pricing(
        self,
        product: Product,
        quantity: float,
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Get level rate and level unit price from product quantity-based pricing.

        Queries ProductQuantityPricing to find the applicable pricing tier
        based on the quantity being purchased.

        Args:
            product: The product to get pricing for
            quantity: The quantity being purchased

        Returns:
            Tuple of (level_rate, level_unit_price):
            - level_rate: Commission rate for this pricing level (if different from base)
            - level_unit_price: Unit price for this quantity level
        """
        from commons.db.v6.core.products import ProductQuantityPricing

        # Query for quantity-based pricing that matches our quantity
        result = await self.session.execute(
            select(ProductQuantityPricing)
            .where(ProductQuantityPricing.product_id == product.id)
            .where(ProductQuantityPricing.quantity_low <= Decimal(str(quantity)))
            .where(ProductQuantityPricing.quantity_high >= Decimal(str(quantity)))
            .order_by(ProductQuantityPricing.quantity_low.desc())
            .limit(1)
        )
        pricing = result.scalar_one_or_none()

        if not pricing:
            return None, None

        level_unit_price = float(pricing.unit_price) if pricing.unit_price else None

        # Calculate level_rate as the discount from base price
        # level_rate = (base_price - level_price) / base_price * 100
        level_rate: float | None = None
        if level_unit_price and product.unit_price:
            base_price = float(product.unit_price)
            if base_price > 0 and level_unit_price < base_price:
                level_rate = ((base_price - level_unit_price) / base_price) * 100

        return level_rate, level_unit_price

    def _calculate_effective_commission_rate(
        self,
        product: Product,
        factory: Factory,
        detail_unit_price: float,
        overage_unit_price: Optional[float],
        customer_commission_rate: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate effective commission rate considering overage.

        Uses:
        - customer_commission_rate if provided (from ProductCpn)
        - product.default_commission_rate as base rate
        - factory.base_commission_rate as fallback
        - factory.rep_overage_share as the percentage of overage commission to rep
        - product.unit_price as base price for weighted calculation

        The effective rate is a weighted average:
        - Base portion gets full commission rate
        - Overage portion gets commission rate * rep_overage_share
        """
        base_rate = self._get_product_commission_rate(
            product, factory, customer_commission_rate
        )

        if not base_rate:
            return None

        # If there's overage, the effective rate is adjusted based on rep's overage share
        if overage_unit_price and detail_unit_price > 0:
            # Get rep's share of overage (stored as percentage, e.g., 100.00 means 100%)
            rep_share = (
                float(factory.rep_overage_share) / 100.0
                if factory.rep_overage_share
                else 1.0
            )

            # Use unit_price as base price
            base_price = float(product.unit_price) if product.unit_price else 0
            if base_price > 0:
                # Weighted average of base commission and overage commission
                # Base portion: base_price / detail_unit_price * base_rate
                # Overage portion: overage_unit_price / detail_unit_price * base_rate * rep_share
                base_portion = base_price / detail_unit_price
                overage_portion = overage_unit_price / detail_unit_price
                effective_rate = (base_rate * base_portion) + (
                    base_rate * rep_share * overage_portion
                )
                return effective_rate

        return base_rate

    async def calculate_quote_overage_by_total(
        self,
        factory_id: UUID,
        line_items: list[dict],
    ) -> OverageRecord:
        """
        Calculate overage using BY_TOTAL method for an entire quote/order.

        BY_TOTAL calculation:
        1. Sum all base prices (product.unit_price * quantity)
        2. Sum all sell prices (detail_unit_price * quantity)
        3. If sell total > base total, overage = sell_total - base_total

        Args:
            factory_id: The factory UUID
            line_items: List of dicts with 'product_id', 'detail_unit_price', 'quantity'

        Returns:
            OverageRecord with total overage calculation
        """
        factory = await self._get_factory(factory_id)
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

        # Calculate totals
        total_base_amount = Decimal("0")
        total_sell_amount = Decimal("0")

        for item in line_items:
            product = await self._get_product(item["product_id"])
            if not product:
                continue

            quantity = Decimal(str(item.get("quantity", 1)))
            detail_unit_price = Decimal(str(item["detail_unit_price"]))
            base_unit_price = product.unit_price or Decimal("0")

            total_base_amount += base_unit_price * quantity
            total_sell_amount += detail_unit_price * quantity

        # Calculate overage on total
        overage_amount: float | None = None
        if total_sell_amount > total_base_amount:
            overage_amount = float(total_sell_amount - total_base_amount)

        # Get rep's share
        rep_share = (
            float(factory.rep_overage_share) / 100.0
            if factory.rep_overage_share
            else 1.0
        )

        # Calculate effective commission rate on total
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
