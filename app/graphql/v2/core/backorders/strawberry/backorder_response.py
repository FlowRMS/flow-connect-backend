from datetime import date
from uuid import UUID

import strawberry


@strawberry.type
class BackorderResponse:
    order_id: UUID
    order_number: str
    product_id: str
    
    # We can try to fetch product name if we join with Product, 
    # but for now let's stick to what's in OrderDetail or easily joinable.
    # OrderDetail has product_id.
    
    customer_id: UUID | None
    
    ordered_quantity: int
    shipped_quantity: float  # Decimal to float
    backordered_quantity: float
    
    due_date: date
    status: str
