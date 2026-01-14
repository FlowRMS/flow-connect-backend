"""
Overage Record Response Type
Contains overage pricing and commission information for a product
"""

from enum import Enum
from typing import Optional

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
    effective_commission_rate: Optional[float] = None
    overage_unit_price: Optional[float] = None
    base_unit_price: Optional[float] = None
    rep_share: Optional[float] = None
    level_rate: Optional[float] = None
    level_unit_price: Optional[float] = None

    # Overage configuration
    overage_type: Optional[OverageTypeEnum] = None

    # Error feedback - populated when calculation cannot be performed
    error_message: Optional[str] = None
    # Indicates if calculation was successful
    success: bool = True
