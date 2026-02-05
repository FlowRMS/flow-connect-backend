from uuid import UUID

import strawberry
from commons.db.v6 import WarehouseStructure
from commons.db.v6.warehouse.warehouse_structure_code import WarehouseStructureCode

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class WarehouseStructureInput(BaseInputGQL[WarehouseStructure]):
    warehouse_id: UUID
    code: WarehouseStructureCode
    level_order: int

    def to_orm_model(self) -> WarehouseStructure:
        return WarehouseStructure(
            warehouse_id=self.warehouse_id,
            code=self.code,
            level_order=self.level_order,
        )
