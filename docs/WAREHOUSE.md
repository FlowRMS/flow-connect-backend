# Warehouse Module - Backend Documentation

## Overview

The warehouse module provides GraphQL API for managing warehouses, members, settings, and location structure. Located at `app/graphql/v2/core/warehouses/`.

## Architecture

```
app/graphql/v2/core/warehouses/
├── __init__.py           # Module exports
├── queries.py            # GraphQL queries
├── mutations.py          # GraphQL mutations
├── repositories/
│   ├── warehouses_repository.py
│   ├── warehouse_members_repository.py
│   ├── warehouse_settings_repository.py
│   └── warehouse_structure_repository.py
├── services/
│   └── warehouse_service.py
└── strawberry/
    ├── warehouse_input.py    # Input types
    └── warehouse_response.py # Response types
```

## Models (from flowbot-commons)

Models are imported from the commons package:
```python
from commons.db.v6 import (
    Warehouse,
    WarehouseMember,
    WarehouseMemberRole,
    WarehouseSettings,
    WarehouseStructure,
    WarehouseStructureCode,
)
```

**Schema:** All tables live in `pywarehouse` PostgreSQL schema.

## Repositories

### WarehousesRepository
CRUD operations for warehouses with eager loading of relations.

```python
class WarehousesRepository:
    async def get_by_id(self, warehouse_id: UUID) -> Warehouse | None
    async def list_all(self) -> list[Warehouse]
    async def create(self, warehouse: Warehouse) -> Warehouse
    async def update(self, warehouse: Warehouse) -> Warehouse
    async def delete(self, warehouse_id: UUID) -> bool
```

### WarehouseMembersRepository
Manages user-warehouse assignments.

### WarehouseSettingsRepository
Manages per-warehouse settings (1:1 with warehouse).

### WarehouseStructureRepository
Manages location hierarchy configuration.

## Service Layer

### WarehouseService
Orchestrates business logic across repositories.

```python
class WarehouseService:
    # Warehouse CRUD
    async def get_by_id(self, warehouse_id: UUID) -> Warehouse
    async def list_all(self) -> list[Warehouse]
    async def create(self, input: WarehouseInput) -> Warehouse
    async def update(self, warehouse_id: UUID, input: WarehouseInput) -> Warehouse
    async def delete(self, warehouse_id: UUID) -> bool

    # Members
    async def add_member(self, warehouse_id: UUID, user_id: UUID, role: WarehouseMemberRole) -> WarehouseMember
    async def remove_member(self, warehouse_id: UUID, user_id: UUID) -> bool
    async def update_member_role(self, warehouse_id: UUID, user_id: UUID, role: WarehouseMemberRole) -> WarehouseMember

    # Settings
    async def update_settings(self, warehouse_id: UUID, input: WarehouseSettingsInput) -> WarehouseSettings

    # Structure
    async def update_structure(self, warehouse_id: UUID, levels: list[WarehouseStructureLevelInput]) -> list[WarehouseStructure]
```

## GraphQL Types

### Inputs (strawberry/warehouse_input.py)

```graphql
input WarehouseInput {
  name: String!
  status: String
  latitude: Decimal
  longitude: Decimal
  description: String
  isActive: Boolean
}

input WarehouseMemberInput {
  userId: UUID!
  role: WarehouseMemberRoleGQL!
}

input WarehouseSettingsInput {
  autoGenerateCodes: Boolean
  requireLocation: Boolean
  showInPickLists: Boolean
  generateQrCodes: Boolean
}

input WarehouseStructureLevelInput {
  code: String!
  levelOrder: Int!
}
```

### Responses (strawberry/warehouse_response.py)

```graphql
type WarehouseResponse {
  id: UUID!
  name: String!
  status: String!
  latitude: Decimal
  longitude: Decimal
  description: String
  isActive: Boolean
  createdAt: DateTime!
  members: [WarehouseMemberResponse!]!
  settings: WarehouseSettingsResponse
  structure: [WarehouseStructureResponse!]!
}
```

### Enums

```python
@strawberry.enum
class WarehouseMemberRoleGQL(IntEnum):
    ADMIN = 1
    MANAGER = 2
    WORKER = 3
```

## GraphQL Queries

```graphql
type Query {
  warehouse(id: UUID!): WarehouseResponse
  warehouses: [WarehouseResponse!]!
}
```

## GraphQL Mutations

```graphql
type Mutation {
  createWarehouse(input: WarehouseInput!): WarehouseResponse!
  updateWarehouse(id: UUID!, input: WarehouseInput!): WarehouseResponse!
  deleteWarehouse(id: UUID!): Boolean!

  addWarehouseMember(warehouseId: UUID!, input: WarehouseMemberInput!): WarehouseMemberResponse!
  removeWarehouseMember(warehouseId: UUID!, userId: UUID!): Boolean!
  updateWarehouseMemberRole(warehouseId: UUID!, userId: UUID!, role: WarehouseMemberRoleGQL!): WarehouseMemberResponse!

  updateWarehouseSettings(warehouseId: UUID!, input: WarehouseSettingsInput!): WarehouseSettingsResponse!
  updateWarehouseStructure(warehouseId: UUID!, levels: [WarehouseStructureLevelInput!]!): [WarehouseStructureResponse!]!
}
```

## Database Schema

Tables in `pywarehouse` schema:
- `warehouses` - Main warehouse table
- `warehouse_members` - User assignments (FK to pyuser.users)
- `warehouse_settings` - Configuration (1:1 with warehouse)
- `warehouse_structure` - Location hierarchy levels

## Migration

After updating flowbot-commons, generate migration:
```bash
alembic revision --autogenerate -m "create pywarehouse schema and tables"
```

The migration should include:
1. `CREATE SCHEMA IF NOT EXISTS pywarehouse`
2. Create all warehouse tables
3. Add foreign keys to pyuser.users

## Dependency Injection

All components use aioinject:
```python
@strawberry.type
class Query:
    @strawberry.field
    @inject
    async def warehouse(
        self,
        id: UUID,
        service: Injected[WarehouseService],
    ) -> WarehouseResponse | None:
        warehouse = await service.get_by_id(id)
        return WarehouseResponse.from_orm_model(warehouse)
```
