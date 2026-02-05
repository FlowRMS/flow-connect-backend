import strawberry
from commons.db.v6.warehouse.warehouse_structure_code import WarehouseStructureCode


@strawberry.input
class WarehouseStructureLevelInput:
    code: WarehouseStructureCode
    level_order: int
