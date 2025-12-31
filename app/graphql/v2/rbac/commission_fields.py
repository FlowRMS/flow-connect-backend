from typing import Final

COMMISSION_FIELDS: Final[frozenset[str]] = frozenset(
    {
        # Balance/aggregate commission fields (camelCase for GraphQL response)
        "commission",
        "commissionRate",
        "commissionDiscount",
        "commissionDiscountRate",
        "totalLineCommission",
        # Check-specific fields
        "enteredCommissionAmount",
        "commissionMonth",
        # Split rate fields
        "splitRate",
        # Product/Factory defaults
        "defaultCommissionRate",
        "baseCommissionRate",
    }
)
