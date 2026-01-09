from enum import Enum

import strawberry


@strawberry.enum
class BulkDeleteEntityType(Enum):
    FACTORIES = "factories"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    ORDERS = "orders"
    INVOICES = "invoices"
    QUOTES = "quotes"
    CHECKS = "checks"
    PRE_OPS = "pre_ops"
