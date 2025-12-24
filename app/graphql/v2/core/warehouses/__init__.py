"""Warehouse module for GraphQL API."""

from app.graphql.v2.core.warehouses.models import (
    Warehouse,
    WarehouseLocation,
    WarehouseMember,
    WarehouseSettings,
    WarehouseStructure,
)
from app.graphql.v2.core.warehouses.mutations import WarehousesMutations
from app.graphql.v2.core.warehouses.queries import WarehousesQueries
from app.graphql.v2.core.warehouses.repositories import (
    WarehouseMembersRepository,
    WarehouseSettingsRepository,
    WarehousesRepository,
    WarehouseStructureRepository,
)
from app.graphql.v2.core.warehouses.services import WarehouseService
from app.graphql.v2.core.warehouses.strawberry import (
    WarehouseInput,
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
    # Models
    "Warehouse",
    "WarehouseMember",
    "WarehouseSettings",
    "WarehouseStructure",
    "WarehouseLocation",
    # Repositories
    "WarehousesRepository",
    "WarehouseMembersRepository",
    "WarehouseSettingsRepository",
    "WarehouseStructureRepository",
    # Services
    "WarehouseService",
    # GraphQL Types
    "WarehouseResponse",
    "WarehouseMemberResponse",
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
