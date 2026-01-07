from commons.db.v6 import (
    LocationProductAssignment,
    Warehouse,
    WarehouseLocation,
    WarehouseMember,
    WarehouseMemberRole,
    WarehouseSettings,
    WarehouseStructure,
)

from app.graphql.v2.core.warehouses.mutations import (
    WarehouseLocationMutations,
    WarehousesMutations,
)
from app.graphql.v2.core.warehouses.queries import (
    WarehouseLocationQueries,
    WarehousesQueries,
)
from app.graphql.v2.core.warehouses.repositories import (
    LocationProductAssignmentRepository,
    WarehouseLocationRepository,
    WarehouseMembersRepository,
    WarehouseRepository,
    WarehouseSettingsRepository,
    WarehouseStructureRepository,
)
from app.graphql.v2.core.warehouses.services import (
    WarehouseLocationAssignmentService,
    WarehouseLocationService,
    WarehouseService,
)
from app.graphql.v2.core.warehouses.strawberry import (
    BulkWarehouseLocationInput,
    LocationProductAssignmentInput,
    LocationProductAssignmentResponse,
    WarehouseInput,
    WarehouseLocationInput,
    WarehouseLocationResponse,
    WarehouseMemberInput,
    WarehouseMemberResponse,
    WarehouseResponse,
    WarehouseSettingsInput,
    WarehouseSettingsResponse,
    WarehouseStructureInput,
    WarehouseStructureLevelInput,
    WarehouseStructureResponse,
)

__all__ = [
    # Models (from commons)
    "LocationProductAssignment",
    "Warehouse",
    "WarehouseLocation",
    "WarehouseMember",
    "WarehouseMemberRole",
    "WarehouseSettings",
    "WarehouseStructure",
    # Repositories
    "LocationProductAssignmentRepository",
    "WarehouseLocationRepository",
    "WarehouseMembersRepository",
    "WarehouseRepository",
    "WarehouseSettingsRepository",
    "WarehouseStructureRepository",
    # Services
    "WarehouseLocationAssignmentService",
    "WarehouseLocationService",
    "WarehouseService",
    # GraphQL Types
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
    # GraphQL Operations
    "WarehouseLocationMutations",
    "WarehouseLocationQueries",
    "WarehousesMutations",
    "WarehousesQueries",
]
