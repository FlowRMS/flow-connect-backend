"""
Overage Service
Calculates overage pricing and effective commission rates
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from flowbot_commons.models import Factory, Product

from app.graphql.common.strawberry.overage_record import OverageRecord


class OverageService:
    """Service for calculating overage pricing and commission rates"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_effective_commission_rate_and_overage(
        self,
        product_id: UUID,
        detail_unit_price: float,
        factory_id: UUID,
        end_user_id: UUID,
    ) -> OverageRecord:
        """
        Calculate effective commission rate and overage unit price for a product.

        Args:
            product_id: The product UUID
            detail_unit_price: The unit price from the quote/order detail
            factory_id: The factory/manufacturer UUID
            end_user_id: The end user customer UUID

        Returns:
            OverageRecord with calculated values
        """
        # Fetch product with overage settings
        product = await self._get_product(product_id)
        if not product:
            return OverageRecord()

        # Fetch factory with overage settings
        factory = await self._get_factory(factory_id)
        if not factory:
            return OverageRecord()

        # Get base values
        base_unit_price = float(product.list_price or 0) if product.list_price else None

        # Check if overage is allowed
        overage_allowed = getattr(product, 'overage_allowed', False) or getattr(factory, 'overage_allowed', False)

        if not overage_allowed:
            # No overage - return basic commission info
            return OverageRecord(
                effective_commission_rate=self._get_product_commission_rate(product),
                overage_unit_price=None,
                base_unit_price=base_unit_price,
                rep_share=None,
                level_rate=None,
                level_unit_price=None,
            )

        # Calculate overage
        overage_unit_price = self._calculate_overage_unit_price(
            product, factory, detail_unit_price
        )

        # Get rep share from factory
        rep_share = float(factory.rep_overage_share) if hasattr(factory, 'rep_overage_share') and factory.rep_overage_share else None

        # Get level rate and price (from product price levels if available)
        level_rate, level_unit_price = self._get_level_pricing(product, detail_unit_price)

        # Calculate effective commission rate
        effective_commission_rate = self._calculate_effective_commission_rate(
            product, factory, detail_unit_price, overage_unit_price
        )

        return OverageRecord(
            effective_commission_rate=effective_commission_rate,
            overage_unit_price=overage_unit_price,
            base_unit_price=base_unit_price,
            rep_share=rep_share,
            level_rate=level_rate,
            level_unit_price=level_unit_price,
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

    def _get_product_commission_rate(self, product: Product) -> Optional[float]:
        """Get the base commission rate from product"""
        if hasattr(product, 'commission_rate') and product.commission_rate:
            return float(product.commission_rate)
        return None

    def _calculate_overage_unit_price(
        self,
        product: Product,
        factory: Factory,
        detail_unit_price: float,
    ) -> Optional[float]:
        """
        Calculate overage unit price.
        Overage = detail_unit_price - base_price (if detail > base)
        """
        # Get overage unit price from product if set
        if hasattr(product, 'overage_unit_price') and product.overage_unit_price:
            return float(product.overage_unit_price)

        # Otherwise calculate based on list price
        base_price = float(product.list_price or 0) if product.list_price else 0

        if detail_unit_price > base_price:
            return detail_unit_price - base_price

        return None

    def _get_level_pricing(
        self,
        product: Product,
        detail_unit_price: float
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Get level rate and level unit price from product price levels.
        Returns (level_rate, level_unit_price)
        """
        # This would need to query price levels if they exist
        # For now, return None as placeholder
        return None, None

    def _calculate_effective_commission_rate(
        self,
        product: Product,
        factory: Factory,
        detail_unit_price: float,
        overage_unit_price: Optional[float],
    ) -> Optional[float]:
        """
        Calculate effective commission rate considering overage.
        """
        base_rate = self._get_product_commission_rate(product)

        if not base_rate:
            # Try to get from factory
            if hasattr(factory, 'default_commission_rate') and factory.default_commission_rate:
                base_rate = float(factory.default_commission_rate)
            else:
                return None

        # If there's overage, the effective rate may be adjusted
        # This is a simplified calculation - actual business logic may vary
        if overage_unit_price and detail_unit_price > 0:
            # Rep share affects the overage commission
            rep_share = float(factory.rep_overage_share) if hasattr(factory, 'rep_overage_share') and factory.rep_overage_share else 1.0

            base_price = float(product.list_price or 0) if product.list_price else 0
            if base_price > 0:
                # Weighted average of base commission and overage commission
                base_portion = base_price / detail_unit_price
                overage_portion = overage_unit_price / detail_unit_price
                effective_rate = (base_rate * base_portion) + (base_rate * rep_share * overage_portion)
                return effective_rate

        return base_rate
