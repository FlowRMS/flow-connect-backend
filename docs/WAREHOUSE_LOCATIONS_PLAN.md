# Warehouse Layout & QR Codes Backend Integration Plan

## How They're Connected

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WAREHOUSE LOCATIONS                                   │
│                                                                             │
│  Warehouse "Main Distribution Center"                                       │
│    │                                                                        │
│    ├── Section A (SEC-001)  ──────────────────────┐                        │
│    │     ├── Aisle 1 (AISLE-001)                  │                        │
│    │     │     ├── Shelf 1A (SHELF-001)           │                        │
│    │     │     │     ├── Bay 01 (BAY-001)         │    Each location       │
│    │     │     │     │     ├── Row 1 (ROW-001)    │    gets a unique       │
│    │     │     │     │     │     ├── Bin A ───────┼──► QR Code that        │
│    │     │     │     │     │     └── Bin B        │    encodes its ID      │
│    │     │     │     │     └── Row 2              │    and path            │
│    │     │     │     └── Bay 02                   │                        │
│    │     │     └── Shelf 1B                       │                        │
│    │     └── Aisle 2                              │                        │
│    └── Section B                                  │                        │
│                                                   │                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           QR CODES                                           │
│                                                                             │
│  ┌─────────────┐   QR Code contains:                                        │
│  │ ▄▄▄▄▄ ▄▄▄▄ │   - Location ID: "BIN-001"                                 │
│  │ █   █ ▄▄▄█ │   - Path: "Section A > Aisle 1 > Shelf 1A > Bay 01 > Bin A"│
│  │ █▄▄▄█ █▄▄▄ │   - Warehouse: "Main Distribution Center"                  │
│  │       ▄▄▄▄ │                                                             │
│  │ ▄▄▄▄▄ █  █ │   When scanned:                                            │
│  │ █   █ █▄▄█ │   → Identifies exact storage location                       │
│  │ █▄▄▄█ ▄▄▄▄ │   → Links to products stored there                         │
│  └─────────────┘   → Used for inventory, picking, receiving                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The Relationship:**
1. **Warehouse Locations** = The hierarchical structure (Section → Aisle → Shelf → Bay → Row → Bin)
2. **QR Codes** = Printable labels for each location that encode the location ID
3. **Same Backend** = Both features use the same `WarehouseLocation` model
4. **Layout Modal** = Create/edit the location hierarchy
5. **QR Modal** = Generate/print QR codes for existing locations

---

## Current State Summary

### What EXISTS in Backend
- `Warehouse` model with basic info (name, status, location, etc.)
- `WarehouseStructure` model - stores which location LEVELS are enabled (Section, Aisle, Shelf, Bay, Row, Bin)
- `WarehouseStructureCode` enum - defines the 6 level types
- `WarehouseMember` and `WarehouseSettings` models
- GraphQL APIs for warehouse CRUD, members, settings, and structure configuration

### What's MISSING in Backend
- **No individual location models** - The backend does NOT have models for actual location instances (e.g., "Section A", "Aisle 3", "Bin A-1-3-B")
- The current `WarehouseStructure` only configures WHICH levels are enabled, not the actual locations themselves
- No `Section`, `Aisle`, `Shelf`, `Bay`, `Row`, `Bin` entity tables

---

## User Decisions

1. **Cascade delete**: YES - Deleting a parent deletes all children
2. **Real QR codes**: YES - Add `qrcode.react` library
3. **Store visual properties**: YES - Persist x, y, width, height in database
4. **Product assignments**: YES - Include product-to-bin model

---

## Detailed Implementation Plan

### Phase 1: Backend Models (flowbot-commons)

#### 1.1 Create WarehouseLocation Model
**File:** `commons/db/v6/warehouse/warehouse_location_model.py`

```python
class WarehouseLocation(PyWarehouseBaseModel):
    __tablename__ = "warehouse_locations"

    warehouse_id: Mapped[UUID]  # FK to Warehouse
    parent_id: Mapped[UUID | None]  # FK to self (null for sections)
    level: Mapped[WarehouseStructureCode]  # SECTION=1, AISLE=2, etc.
    name: Mapped[str]  # "Section A", "Aisle 1"
    code: Mapped[str | None]  # Optional code like "SEC-001"
    description: Mapped[str | None]
    is_active: Mapped[bool] = True
    sort_order: Mapped[int] = 0

    # Visual properties
    x: Mapped[float | None]
    y: Mapped[float | None]
    width: Mapped[float | None]
    height: Mapped[float | None]
    rotation: Mapped[float | None]

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(back_populates="locations")
    parent: Mapped["WarehouseLocation"] = relationship(remote_side=[id])
    children: Mapped[list["WarehouseLocation"]] = relationship(
        cascade="all, delete-orphan"  # CASCADE DELETE
    )
    product_assignments: Mapped[list["LocationProductAssignment"]] = relationship(
        cascade="all, delete-orphan"
    )
```

#### 1.2 Create LocationProductAssignment Model
**File:** `commons/db/v6/warehouse/location_product_assignment_model.py`

```python
class LocationProductAssignment(PyWarehouseBaseModel):
    __tablename__ = "location_product_assignments"

    location_id: Mapped[UUID]  # FK to WarehouseLocation (bins only)
    product_id: Mapped[UUID]  # FK to Product
    quantity: Mapped[int] = 0

    # Relationships
    location: Mapped["WarehouseLocation"] = relationship(back_populates="product_assignments")
```

#### 1.3 Update Warehouse Model
Add locations relationship to existing Warehouse model.

### Phase 2: Database Migration

**File:** `migrations/versions/xxx_add_warehouse_locations.py`

Create tables:
- `pywarehouse.warehouse_locations`
- `pywarehouse.location_product_assignments`

With cascade delete constraints.

### Phase 3: Backend GraphQL APIs (flow-py-backend)

#### 3.1 Repository
**File:** `app/graphql/v2/core/warehouses/repositories/warehouse_location_repository.py`

Methods:
- `get_by_id(id)` - Single location
- `list_by_warehouse(warehouse_id)` - All locations flat
- `get_tree(warehouse_id)` - Hierarchical with children loaded
- `get_children(parent_id)` - Direct children
- `create(location)` - Insert
- `update(id, updates)` - Update
- `delete(id)` - Delete (cascade handled by DB)
- `bulk_upsert(warehouse_id, locations)` - Batch save

#### 3.2 Service
**File:** `app/graphql/v2/core/warehouses/services/warehouse_location_service.py`

Business logic:
- Validate parent-child level hierarchy (Section > Aisle > Shelf > Bay > Row > Bin)
- Generate codes if auto_generate_codes is enabled
- Validate location exists before product assignment

#### 3.3 GraphQL Types
**Files:**
- `strawberry/warehouse_location_input.py`
- `strawberry/warehouse_location_response.py`
- `strawberry/location_product_assignment_input.py`
- `strawberry/location_product_assignment_response.py`

#### 3.4 Queries
**File:** `queries/warehouse_location_queries.py`

```graphql
warehouseLocations(warehouseId: UUID!): [WarehouseLocation!]!
warehouseLocationTree(warehouseId: UUID!): [WarehouseLocation!]!  # With nested children
warehouseLocation(id: UUID!): WarehouseLocation
```

#### 3.5 Mutations
**File:** `mutations/warehouse_location_mutations.py`

```graphql
createWarehouseLocation(input: WarehouseLocationInput!): WarehouseLocation!
updateWarehouseLocation(id: UUID!, input: WarehouseLocationInput!): WarehouseLocation!
deleteWarehouseLocation(id: UUID!): Boolean!
bulkSaveWarehouseLocations(warehouseId: UUID!, locations: [WarehouseLocationInput!]!): [WarehouseLocation!]!

# Product assignments
assignProductToLocation(locationId: UUID!, productId: UUID!, quantity: Int!): LocationProductAssignment!
removeProductFromLocation(locationId: UUID!, productId: UUID!): Boolean!
updateProductQuantity(locationId: UUID!, productId: UUID!, quantity: Int!): LocationProductAssignment!
```

### Phase 4: Frontend API Integration (flow-crm)

#### 4.1 API Client
**File:** `components/warehouse/settings/api/warehouseLocationsApi.ts`

Functions:
- `fetchWarehouseLocations(warehouseId)`
- `fetchWarehouseLocationTree(warehouseId)`
- `createWarehouseLocation(input)`
- `updateWarehouseLocation(id, input)`
- `deleteWarehouseLocation(id)`
- `bulkSaveWarehouseLocations(warehouseId, locations)`
- `assignProductToLocation(locationId, productId, quantity)`
- `removeProductFromLocation(locationId, productId)`

#### 4.2 React Query Hooks
**File:** `components/warehouse/settings/api/useWarehouseLocationsApi.ts`

Hooks:
- `useWarehouseLocations(warehouseId)`
- `useWarehouseLocationTree(warehouseId)`
- `useCreateLocation()`
- `useUpdateLocation()`
- `useDeleteLocation()`
- `useBulkSaveLocations()`

### Phase 5: Update Layout Modal

#### 5.1 Update useLocationManagement Hook
**File:** `components/warehouse/layout/hooks/useLocationManagement.ts`

Changes:
- Replace mock data initialization with API fetch
- Add loading/error states
- Wrap CRUD operations with API calls
- Add save button that calls `bulkSaveWarehouseLocations`

#### 5.2 Update buildLocationTree
**File:** `components/warehouse/layout/utils.ts`

Change to accept API response format instead of mock data.

### Phase 6: Update QR Codes Modal

#### 6.1 Install qrcode.react
```bash
pnpm add qrcode.react
```

#### 6.2 Update QR Generator
**File:** `components/warehouse/qr-codes/utils/qrCodeGenerator.ts`

Replace hash-based patterns with actual QR code generation using `qrcode.react`.

#### 6.3 Update locationBuilder
**File:** `components/warehouse/qr-codes/utils/locationBuilder.ts`

Change to use API data instead of mock data.

---

## File Changes Summary

### New Files (Backend)
1. `flowbot-commons/commons/db/v6/warehouse/warehouse_location_model.py`
2. `flowbot-commons/commons/db/v6/warehouse/location_product_assignment_model.py`
3. `flow-py-backend/migrations/versions/xxx_add_warehouse_locations.py`
4. `flow-py-backend/app/graphql/v2/core/warehouses/repositories/warehouse_location_repository.py`
5. `flow-py-backend/app/graphql/v2/core/warehouses/services/warehouse_location_service.py`
6. `flow-py-backend/app/graphql/v2/core/warehouses/strawberry/warehouse_location_*.py`
7. `flow-py-backend/app/graphql/v2/core/warehouses/queries/warehouse_location_queries.py`
8. `flow-py-backend/app/graphql/v2/core/warehouses/mutations/warehouse_location_mutations.py`

### New Files (Frontend)
1. `flow-crm/components/warehouse/settings/api/warehouseLocationsApi.ts`
2. `flow-crm/components/warehouse/settings/api/useWarehouseLocationsApi.ts`

### Modified Files (Frontend)
1. `flow-crm/components/warehouse/layout/hooks/useLocationManagement.ts`
2. `flow-crm/components/warehouse/layout/utils.ts`
3. `flow-crm/components/warehouse/qr-codes/utils/locationBuilder.ts`
4. `flow-crm/components/warehouse/qr-codes/utils/qrCodeGenerator.ts`
5. `flow-crm/package.json` (add qrcode.react)
