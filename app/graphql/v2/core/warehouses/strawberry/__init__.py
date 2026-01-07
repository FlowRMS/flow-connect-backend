"""Warehouse Strawberry types."""

from app.graphql.v2.core.warehouses.strawberry.warehouse_input import (
    WarehouseInput,
    WarehouseMemberInput,
    WarehouseSettingsInput,
    WarehouseStructureInput,
    WarehouseStructureLevelInput,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_input import (
    BulkWarehouseLocationInput,
    LocationProductAssignmentInput,
    WarehouseLocationInput,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_response import (
    LocationProductAssignmentResponse,
    WarehouseLocationResponse,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_response import (
    WarehouseMemberResponse,
    WarehouseResponse,
    WarehouseSettingsResponse,
    WarehouseStructureResponse,
)

__all__ = [
    "BulkWarehouseLocationInput",
    "LocationProductAssignmentInput",
    "LocationProductAssignmentResponse",
    "WarehouseInput",
    "WarehouseLocationInput",
    "WarehouseLocationResponse",
    "WarehouseMemberInput",
    "WarehouseMemberResponse",
    "WarehouseResponse",
    "WarehouseSettingsInput",
    "WarehouseSettingsResponse",
    "WarehouseStructureInput",
    "WarehouseStructureLevelInput",
    "WarehouseStructureResponse",
]
