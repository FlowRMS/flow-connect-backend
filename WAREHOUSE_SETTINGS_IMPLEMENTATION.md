# Warehouse Settings Backend Implementation

## Status: In Progress

Last Updated: 2024-12-24

---

## Overview

Create backend GraphQL endpoints for the warehouse settings page:
- Warehouses (CRUD + workers + location levels)
- Shipping Carriers (full configuration)
- Container Types (with ordering)
- Warehouse Locations (for layout/QR - Phase 2)

---

## Progress Tracker

### Step 1: Database Migrations
- [x] Add columns to `shipping_carriers` table
- [x] Create `warehouse_locations` table
- [x] Migration file created: `alembic/versions/20251224_warehouse_settings.py`

### Step 2: Warehouses Module
- [x] Create SQLAlchemy models (Warehouse, WarehouseMember, WarehouseSettings, WarehouseStructure)
- [x] Create repository
- [x] Create service
- [x] Create Strawberry types (response, input)
- [x] Create queries
- [x] Create mutations
- [ ] Test in GraphQL playground

### Step 3: Container Types Module
- [x] Create SQLAlchemy model
- [x] Create repository
- [x] Create service
- [x] Create Strawberry types
- [x] Create queries
- [x] Create mutations
- [x] Add reorder mutation
- [ ] Test in GraphQL playground

### Step 4: Shipping Carriers Module
- [x] Create SQLAlchemy model (with all new columns)
- [x] Create repository
- [x] Create service
- [x] Create Strawberry types
- [x] Create queries
- [x] Create mutations
- [ ] Test in GraphQL playground

### Step 5: Warehouse Locations Module (Phase 2)
- [ ] Create SQLAlchemy model
- [ ] Create repository with hierarchy support
- [ ] Create service
- [ ] Create Strawberry types
- [ ] Create queries (with path building)
- [ ] Create mutations (including bulk create)
- [ ] Test in GraphQL playground

### Step 6: Frontend Integration
- [ ] Update useWarehouseSettings hook
- [ ] Update useShippingCarriers hook
- [ ] Update useContainerTypes hook
- [ ] Test end-to-end

---

## Database Schema

### Existing Tables

**pycrm.warehouses**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| name | varchar(255) | NOT NULL |
| status | varchar(50) | NOT NULL |
| address_line | varchar(500) | nullable |
| city | varchar(100) | nullable |
| state | varchar(100) | nullable |
| zip | varchar(20) | nullable |
| created_at | timestamptz | NOT NULL |
| address_line_2 | varchar | nullable |
| country | varchar | nullable |
| latitude | numeric(10,7) | nullable |
| longitude | numeric(10,7) | nullable |
| description | text | nullable |
| is_active | boolean | default true |

**pycrm.warehouse_members**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| warehouse_id | uuid | FK |
| user_id | uuid | NOT NULL |
| role | integer | 1=worker, 2=manager |
| role_name | varchar(20) | nullable |
| created_at | timestamptz | nullable |
| created_by_id | uuid | nullable |

**pycrm.warehouse_settings**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| warehouse_id | uuid | FK (unique) |
| auto_generate_codes | boolean | default false |
| require_location | boolean | default true |
| show_in_pick_lists | boolean | default true |
| generate_qr_codes | boolean | default false |

**pycrm.warehouse_structure** (location level config)
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| warehouse_id | uuid | FK |
| code | varchar(100) | e.g., 'section', 'aisle' |
| level_order | integer | 1, 2, 3... |

**pycrm.container_types**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| name | varchar | NOT NULL |
| length | numeric(10,2) | NOT NULL |
| width | numeric(10,2) | NOT NULL |
| height | numeric(10,2) | NOT NULL |
| weight | numeric(10,2) | tare weight |
| order | integer | display order |
| created_at | timestamptz | |

**pycrm.shipping_carriers** (needs columns added)
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| name | varchar | NOT NULL |
| account_number | varchar | nullable |
| is_active | boolean | default true |
| created_at | timestamptz | |

### Migrations Required

**1. Add columns to shipping_carriers:**
```sql
ALTER TABLE pycrm.shipping_carriers
  ADD COLUMN code VARCHAR(50),
  ADD COLUMN billing_address TEXT,
  ADD COLUMN payment_terms VARCHAR(50),
  ADD COLUMN api_key VARCHAR(255),
  ADD COLUMN api_endpoint VARCHAR(500),
  ADD COLUMN tracking_url_template VARCHAR(500),
  ADD COLUMN contact_name VARCHAR(255),
  ADD COLUMN contact_phone VARCHAR(50),
  ADD COLUMN contact_email VARCHAR(255),
  ADD COLUMN service_types JSONB,
  ADD COLUMN default_service_type VARCHAR(100),
  ADD COLUMN max_weight NUMERIC(10,2),
  ADD COLUMN max_dimensions VARCHAR(50),
  ADD COLUMN residential_surcharge NUMERIC(10,2),
  ADD COLUMN fuel_surcharge_percent NUMERIC(5,2),
  ADD COLUMN pickup_schedule VARCHAR(255),
  ADD COLUMN pickup_location VARCHAR(255),
  ADD COLUMN remarks TEXT,
  ADD COLUMN internal_notes TEXT;
```

**2. Create warehouse_locations table:**
```sql
CREATE TABLE pycrm.warehouse_locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  warehouse_id UUID NOT NULL REFERENCES pycrm.warehouses(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES pycrm.warehouse_locations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('section', 'aisle', 'shelf', 'bay', 'row', 'bin')),
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  x NUMERIC(10,2),
  y NUMERIC(10,2),
  width NUMERIC(10,2),
  height NUMERIC(10,2),
  rotation NUMERIC(5,2) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ix_warehouse_locations_warehouse_id ON pycrm.warehouse_locations(warehouse_id);
CREATE INDEX ix_warehouse_locations_parent_id ON pycrm.warehouse_locations(parent_id);
CREATE INDEX ix_warehouse_locations_type ON pycrm.warehouse_locations(type);
```

---

## File Structure

```
app/graphql/v2/core/warehouses/
├── __init__.py
├── models/
│   └── warehouse.py
├── repositories/
│   ├── __init__.py
│   └── warehouses_repository.py
├── services/
│   ├── __init__.py
│   └── warehouse_service.py
├── strawberry/
│   ├── __init__.py
│   ├── warehouse_response.py
│   ├── warehouse_input.py
│   ├── warehouse_member_response.py
│   └── warehouse_structure_response.py
├── queries/
│   ├── __init__.py
│   └── warehouses_queries.py
└── mutations/
    ├── __init__.py
    └── warehouses_mutations.py

app/graphql/v2/core/container_types/
├── __init__.py
├── models/
│   └── container_type.py
├── repositories/
│   ├── __init__.py
│   └── container_types_repository.py
├── services/
│   ├── __init__.py
│   └── container_type_service.py
├── strawberry/
│   ├── __init__.py
│   ├── container_type_response.py
│   └── container_type_input.py
├── queries/
│   ├── __init__.py
│   └── container_types_queries.py
└── mutations/
    ├── __init__.py
    └── container_types_mutations.py

app/graphql/v2/core/shipping_carriers/
├── __init__.py
├── models/
│   └── shipping_carrier.py
├── repositories/
│   ├── __init__.py
│   └── shipping_carriers_repository.py
├── services/
│   ├── __init__.py
│   └── shipping_carrier_service.py
├── strawberry/
│   ├── __init__.py
│   ├── shipping_carrier_response.py
│   └── shipping_carrier_input.py
├── queries/
│   ├── __init__.py
│   └── shipping_carriers_queries.py
└── mutations/
    ├── __init__.py
    └── shipping_carriers_mutations.py
```

---

## GraphQL Operations

### Warehouses
- `Query.warehouses` - List all warehouses
- `Query.warehouse(id)` - Get warehouse with settings, members, structure
- `Mutation.createWarehouse(input)` - Create warehouse
- `Mutation.updateWarehouse(id, input)` - Update warehouse
- `Mutation.deleteWarehouse(id)` - Delete warehouse
- `Mutation.assignWorkerToWarehouse(warehouseId, userId, role)`
- `Mutation.updateWorkerRole(warehouseId, userId, role)`
- `Mutation.removeWorkerFromWarehouse(warehouseId, userId)`
- `Mutation.updateWarehouseStructure(warehouseId, levels)` - Update enabled levels

### Container Types
- `Query.containerTypes` - List all (ordered)
- `Query.containerType(id)` - Get single
- `Mutation.createContainerType(input)`
- `Mutation.updateContainerType(id, input)`
- `Mutation.deleteContainerType(id)`
- `Mutation.reorderContainerTypes(orderedIds)`

### Shipping Carriers
- `Query.shippingCarriers` - List all
- `Query.shippingCarrier(id)` - Get single
- `Mutation.createShippingCarrier(input)`
- `Mutation.updateShippingCarrier(id, input)`
- `Mutation.deleteShippingCarrier(id)`

### Warehouse Locations (Phase 2)
- `Query.warehouseLocations(warehouseId)` - Get hierarchy
- `Query.warehouseLocation(id)` - Get with path
- `Mutation.createWarehouseLocation(input)`
- `Mutation.updateWarehouseLocation(id, input)`
- `Mutation.deleteWarehouseLocation(id)`
- `Mutation.bulkCreateLocations(warehouseId, locations)`

---

## Field Mappings (DB -> GraphQL)

| DB Column | GraphQL Field |
|-----------|---------------|
| address_line | addressLine1 |
| address_line_2 | addressLine2 |
| zip | postalCode |
| is_active | isActive |
| created_at | createdAt |
| account_number | accountNumber |
| parent_id | parentId |

---

## Testing

```bash
# Start backend
uv run uvicorn app.main:app --reload --port 5555

# GraphQL Playground
http://localhost:5555/graphql
```

---

## Notes

- Using local SQLAlchemy models (not from commons) since warehouse tables are custom
- Following v6 patterns from customers/factories modules
- Auto-discovery will register repositories/services/queries/mutations
- Frontend currently uses mock data - will update hooks after backend is ready
