from decimal import Decimal

import strawberry
from commons.db.v6 import Warehouse

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class WarehouseInput(BaseInputGQL[Warehouse]):
    """Input type for creating/updating warehouses.

    Note: Address information is managed separately via the Address model
    using source_id = warehouse.id and source_type = FACTORY.
    """

    name: str
    status: str = "active"
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    description: str | None = None
    is_active: bool = True

    def to_orm_model(self) -> Warehouse:
        return Warehouse(
            name=self.name,
            status=self.status,
            latitude=self.latitude,
            longitude=self.longitude,
            description=self.description,
            is_active=self.is_active,
        )
