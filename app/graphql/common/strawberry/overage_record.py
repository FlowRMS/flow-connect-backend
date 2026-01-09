"""
Overage Record Response Type
Contains overage pricing and commission information for a product
"""

from typing import Optional

import strawberry


@strawberry.type
class OverageRecord:
    """
    Overage calculation result for a product.
    Used in quotes and orders to calculate overage pricing.
    """
    effective_commission_rate: Optional[float] = None
    overage_unit_price: Optional[float] = None
    base_unit_price: Optional[float] = None
    rep_share: Optional[float] = None
    level_rate: Optional[float] = None
    level_unit_price: Optional[float] = None


@strawberry.enum
class OverageTypeEnum:
    """Type of overage calculation"""
    BY_LINE = "BY_LINE"
    BY_TOTAL = "BY_TOTAL"
