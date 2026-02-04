from enum import Enum

import strawberry


@strawberry.enum
class OverageTypeEnum(Enum):
    """
    Type of overage calculation.

    BY_LINE: Calculate overage on each line item individually.
             Overage = (detail_unit_price - product_unit_price) per line.

    BY_TOTAL: Calculate overage on the total quote/order amount.
              Overage = (total_amount - sum(product_unit_price * qty)).
    """

    BY_LINE = "BY_LINE"
    BY_TOTAL = "BY_TOTAL"


@strawberry.type
class OverageRecord:
    """
    Overage calculation result for a product or quote.
    Used in quotes and orders to calculate overage pricing.
    """

    # Calculation results
    effective_commission_rate: float | None = None
    overage_unit_price: float | None = None
    base_unit_price: float | None = None
    rep_share: float | None = None
    level_rate: float | None = None
    level_unit_price: float | None = None

    # Overage configuration
    overage_type: OverageTypeEnum | None = None

    # Error feedback - populated when calculation cannot be performed
    error_message: str | None = None
    # Indicates if calculation was successful
    success: bool = True
