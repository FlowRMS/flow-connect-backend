"""Warehouse module for GraphQL API."""

from commons.db.v6 import (
    Warehouse,
    WarehouseMember,
    WarehouseMemberRole,
    WarehouseSettings,
    WarehouseStructure,
)

from app.graphql.v2.core.warehouses.mutations import WarehousesMutations
from app.graphql.v2.core.warehouses.queries import WarehousesQueries
from app.graphql.v2.core.warehouses.repositories import (
    WarehouseMembersRepository,
    WarehouseRepository,
    WarehouseSettingsRepository,
    WarehouseStructureRepository,
)
from app.graphql.v2.core.warehouses.services import WarehouseService
from app.graphql.v2.core.warehouses.strawberry import (
    WarehouseInput,
    WarehouseMemberInput,
    WarehouseMemberResponse,
    WarehouseMemberRole,
    WarehouseResponse,
    WarehouseSettingsInput,
    WarehouseSettingsResponse,
    WarehouseStructureInput,
    WarehouseStructureLevelInput,
    WarehouseStructureResponse,
)

__all__ = [
    # Models (from commons)
    "Warehouse",
    "WarehouseMember",
    "WarehouseMemberRole",
    "WarehouseSettings",
    "WarehouseStructure",
    # Repositories
    "WarehouseRepository",
    "WarehouseMembersRepository",
    "WarehouseSettingsRepository",
    "WarehouseStructureRepository",
    # Services
    "WarehouseService",
    # GraphQL Types
    "WarehouseResponse",
    "WarehouseMemberResponse",
    "WarehouseMemberRole",
    "WarehouseSettingsResponse",
    "WarehouseStructureResponse",
    "WarehouseInput",
    "WarehouseMemberInput",
    "WarehouseSettingsInput",
    "WarehouseStructureInput",
    "WarehouseStructureLevelInput",
    # GraphQL Operations
    "WarehousesQueries",
    "WarehousesMutations",
]
