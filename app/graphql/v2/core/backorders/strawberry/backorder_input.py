from decimal import Decimal
from uuid import UUID
import strawberry

@strawberry.input
class BackorderItemInput:
    product_id: UUID
    quantity: Decimal
