import strawberry


@strawberry.type
class InventoryStatsResponse:
    total_products: int
    total_quantity: int
    available_quantity: int
    reserved_quantity: int
    low_stock_count: int
    picking_quantity: int
