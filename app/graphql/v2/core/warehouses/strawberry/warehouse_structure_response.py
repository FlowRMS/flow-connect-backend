from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import WarehouseStructure
from commons.db.v6.warehouse.warehouse_structure_code import WarehouseStructureCode

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class WarehouseStructureResponse(DTOMixin[WarehouseStructure]):
    _instance: strawberry.Private[WarehouseStructure]
    id: UUID
    warehouse_id: UUID
    code: WarehouseStructureCode
    level_order: int

    @classmethod
    def from_orm_model(cls, model: WarehouseStructure) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            code=model.code,
            level_order=model.level_order,
        )
