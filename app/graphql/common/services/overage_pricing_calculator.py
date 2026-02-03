from commons.db.v6.core.factories import Factory
from commons.db.v6.core.products import Product


class OveragePricingCalculator:
    @staticmethod
    def get_product_commission_rate(
        product: Product,
        factory: Factory | None = None,
        customer_rate_override: float | None = None,
    ) -> float | None:
        if customer_rate_override is not None:
            return customer_rate_override

        if product.default_commission_rate:
            return float(product.default_commission_rate)

        if factory and factory.base_commission_rate:
            return float(factory.base_commission_rate)

        return None

    @staticmethod
    def calculate_overage_unit_price(
        product: Product,
        detail_unit_price: float,
    ) -> float | None:
        base_price = float(product.unit_price) if product.unit_price else 0

        if detail_unit_price > base_price:
            return detail_unit_price - base_price

        return None

    @staticmethod
    def calculate_level_rate(
        level_unit_price: float | None,
        base_unit_price: float | None,
    ) -> float | None:
        if level_unit_price and base_unit_price and base_unit_price > 0:
            if level_unit_price < base_unit_price:
                return ((base_unit_price - level_unit_price) / base_unit_price) * 100
        return None

    @staticmethod
    def calculate_effective_commission_rate(
        product: Product,
        factory: Factory,
        detail_unit_price: float,
        overage_unit_price: float | None,
        customer_commission_rate: float | None = None,
    ) -> float | None:
        base_rate = OveragePricingCalculator.get_product_commission_rate(
            product, factory, customer_commission_rate
        )

        if not base_rate:
            return None

        if overage_unit_price and detail_unit_price > 0:
            rep_share = (
                float(factory.rep_overage_share) / 100.0
                if factory.rep_overage_share
                else 1.0
            )

            base_price = float(product.unit_price) if product.unit_price else 0
            if base_price > 0:
                base_portion = base_price / detail_unit_price
                overage_portion = overage_unit_price / detail_unit_price
                effective_rate = (base_rate * base_portion) + (
                    base_rate * rep_share * overage_portion
                )
                return effective_rate

        return base_rate
