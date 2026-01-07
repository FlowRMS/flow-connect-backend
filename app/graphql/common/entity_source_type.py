from enum import Enum

import strawberry


@strawberry.enum
class EntitySourceType(Enum):
    PRE_OPPORTUNITIES = "pre_opportunities"
    QUOTES = "quotes"
    ORDERS = "orders"
    INVOICES = "invoices"
    CHECKS = "checks"
