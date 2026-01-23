from enum import Enum

import strawberry


@strawberry.enum
class BulkDeleteEntityType(Enum):
    FACTORIES = "factories"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    ORDERS = "orders"
    INVOICES = "invoices"
    CREDITS = "credits"
    QUOTES = "quotes"
    CHECKS = "checks"
    PRE_OPS = "pre_ops"
    STATEMENTS = "statements"
