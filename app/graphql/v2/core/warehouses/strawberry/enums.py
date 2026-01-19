"""Strawberry enum registrations for warehouses module."""

import strawberry
from commons.db.v6.warehouse.warehouse_member_role import (
    WarehouseMemberRole as _WarehouseMemberRole,
)
from commons.db.v6.warehouse.warehouse_structure_code import (
    WarehouseStructureCode as _WarehouseStructureCode,
)

WarehouseMemberRole = strawberry.enum(_WarehouseMemberRole)
WarehouseStructureCode = strawberry.enum(_WarehouseStructureCode)

__all__ = [
    "WarehouseMemberRole",
    "WarehouseStructureCode",
]
