from decimal import Decimal

import strawberry


@strawberry.type
class InventoryStatsResponse:
    total_products: int
    total_quantity: Decimal
    available_quantity: Decimal
    reserved_quantity: Decimal
    low_stock_count: int
    picking_quantity: Decimal
