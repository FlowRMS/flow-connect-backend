# Warehouse Settings Development Notes

This document captures the development process, PR review feedback, fixes applied, and architectural decisions for the warehouse settings feature. Use this as a reference for building future sections.

---

## Table of Contents
1. [Feature Overview](#feature-overview)
2. [Architecture Decisions](#architecture-decisions)
3. [PR Review Feedback & Fixes](#pr-review-feedback--fixes)
4. [Schema Structure](#schema-structure)
5. [Development Environment Setup](#development-environment-setup)
6. [Known Issues & Workarounds](#known-issues--workarounds)
7. [Testing Results](#testing-results)
8. [Checklist for Future Sections](#checklist-for-future-sections)

---

## Feature Overview

### What We Built
Warehouse settings backend with 25 GraphQL endpoints across 3 entity groups:

| Entity | Endpoints | Schema |
|--------|-----------|--------|
| Container Types | 6 (list, get, create, update, delete, reorder) | pywarehouse |
| Shipping Carriers | 6 (list, get, search, create, update, delete) | pywarehouse |
| Warehouses | 13 (CRUD + members + settings + structure) | pywarehouse |

### Repositories Involved
1. **flowbot-commons** - SQLAlchemy models
2. **flow-py-backend** - GraphQL endpoints, services, repositories
3. **flow-crm** - Frontend (not modified in this PR)

---

## Architecture Decisions

### Schema Choice: pywarehouse (NOT pycrm)

**Initial approach:** Container types and shipping carriers were placed in `pycrm` schema because they seemed like CRM-related entities.

**PR Review feedback:** "the alembic files still show pycrm"

**Decision:** Move ALL warehouse settings tables to `pywarehouse` schema for consistency.

**Rationale:**
- Container types and shipping carriers are ONLY used in warehouse settings currently
- Keeping all warehouse-related tables in one schema simplifies maintenance
- If these entities need to be shared later, we can create views or move them

### Base Model Pattern

Models in flowbot-commons use base classes that determine the schema:

```python
# For pycrm schema tables
class MyModel(PyCRMBaseModel, ...):
    pass

# For pywarehouse schema tables
class MyModel(PyWarehouseBaseModel, ...):
    pass
```

The base class automatically sets `__table_args__ = {"schema": "pywarehouse"}`.

### Field Naming Conventions

**PR Review feedback:** Changed field names for consistency:
- `order` → `position` (for display ordering in UI)
- `api_key` type: `String(255)` → `Text` (API keys can be long)

**Mixin columns:** When using mixins like `HasCreatedBy`, the column is `created_by_id` (not `created_by`).

---

## PR Review Feedback & Fixes

### Round 1: Initial Review

| Feedback | Fix Applied |
|----------|-------------|
| "order→position" | Renamed `order` field to `position` in ContainerType model |
| "api_key to Text" | Changed `api_key` from `String(255)` to `Text` |
| "removed contact fields" | Removed contact-related columns (contacts stored via Contact model with LinkRelation) |
| "service_types to dict" | Changed `service_types` to JSONB type |

### Round 2: Schema Review

| Feedback | Fix Applied |
|----------|-------------|
| "alembic files still show pycrm" | Moved container_types and shipping_carriers to pywarehouse schema |

**Files changed:**
- `alembic/versions/20251230_warehouse_settings.py` - Changed `schema="pycrm"` to `schema="pywarehouse"`
- `container_type_model.py` - Changed `PyCRMBaseModel` to `PyWarehouseBaseModel`
- `shipping_carrier_model.py` - Changed `PyCRMBaseModel` to `PyWarehouseBaseModel`

### Round 3: Type Fixes

| Issue | Fix Applied |
|-------|-------------|
| Strawberry doesn't support `dict` type | Changed `service_types: dict` to `service_types: JSON` using `from strawberry.scalars import JSON` |
| Column name mismatch | Changed `created_by` to `created_by_id` to match `HasCreatedBy` mixin |

---

## Schema Structure

### Final Database Schema

All tables in `pywarehouse` schema:

```sql
-- Container dimensions and weights
pywarehouse.container_types (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    length NUMERIC(10,2) NOT NULL,
    width NUMERIC(10,2) NOT NULL,
    height NUMERIC(10,2) NOT NULL,
    weight NUMERIC(10,2) NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
)

-- Shipping carrier configuration
pywarehouse.shipping_carriers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    account_number VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    payment_terms VARCHAR(50),
    api_key TEXT,
    api_endpoint TEXT,
    tracking_url_template VARCHAR(500),
    service_types JSONB,
    default_service_type VARCHAR(100),
    max_weight NUMERIC(10,2),
    max_dimensions VARCHAR(50),
    residential_surcharge NUMERIC(10,2),
    fuel_surcharge_percent NUMERIC(5,2),
    pickup_schedule VARCHAR(255),
    pickup_location VARCHAR(255),
    remarks TEXT,
    internal_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
)

-- Warehouse locations
pywarehouse.warehouses (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50),
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
)

-- Warehouse team members
pywarehouse.warehouse_members (
    id UUID PRIMARY KEY,
    warehouse_id UUID NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES pyuser.users(id),
    role INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by_id UUID
)

-- Warehouse configuration settings
pywarehouse.warehouse_settings (
    id UUID PRIMARY KEY,
    warehouse_id UUID NOT NULL UNIQUE REFERENCES warehouses(id) ON DELETE CASCADE,
    auto_generate_codes BOOLEAN DEFAULT false,
    require_location BOOLEAN DEFAULT true,
    show_in_pick_lists BOOLEAN DEFAULT true,
    generate_qr_codes BOOLEAN DEFAULT false
)

-- Location level configuration
pywarehouse.warehouse_structure (
    id UUID PRIMARY KEY,
    warehouse_id UUID NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    code INTEGER NOT NULL,
    level_order INTEGER NOT NULL
)
```

### Model File Structure

```
flowbot-commons/
└── commons/db/v6/
    ├── crm/
    │   ├── container_types/
    │   │   ├── __init__.py
    │   │   └── container_type_model.py  # Uses PyWarehouseBaseModel
    │   └── shipping_carriers/
    │       ├── __init__.py
    │       └── shipping_carrier_model.py  # Uses PyWarehouseBaseModel
    └── warehouse/
        ├── __init__.py
        ├── warehouse_model.py
        ├── warehouse_member_model.py
        ├── warehouse_member_role.py
        ├── warehouse_settings_model.py
        └── warehouse_structure_model.py

flow-py-backend/
└── app/graphql/v2/core/
    ├── container_types/
    │   ├── mutations/
    │   ├── queries/
    │   ├── repositories/
    │   ├── services/
    │   └── strawberry/
    ├── shipping_carriers/
    │   ├── mutations/
    │   ├── queries/
    │   ├── repositories/
    │   ├── services/
    │   └── strawberry/
    └── warehouses/
        ├── docs/  # Documentation
        ├── mutations/
        ├── queries/
        ├── repositories/
        ├── services/
        └── strawberry/
```

---

## Development Environment Setup

### Prerequisites
1. Redis running locally (port 6379)
2. Access to Neon database branch
3. Valid WorkOS authentication token

### Database Connection

Use `postgresql+asyncpg://` driver (NOT `postgresql://`):

```bash
# .env.staging
PG_URL=postgresql+asyncpg://user:password@host/database?ssl=require
```

### Multi-Tenant Setup

The backend requires a `public.tenants` table for tenant routing:

```python
# tenants table format
# database = hostname ONLY (not full URL)
# url = database name (also used as tenant_name)

await conn.execute('''
    INSERT INTO public.tenants (id, initialize, name, url, database, read_only_database, username, alembic_version)
    VALUES (
        'uuid-here',
        true,
        'app',
        'app',  -- database name
        'ep-xxx-pooler.region.aws.neon.tech',  -- hostname only
        'ep-xxx-pooler.region.aws.neon.tech',
        'neondb_owner',
        'head'
    )
''')
```

### Running the Backend

```bash
cd flow-py-backend
uv run python main.py --env staging
# Server runs at http://127.0.0.1:8006
# GraphQL endpoint: http://127.0.0.1:8006/graphql
```

### Authentication Headers

```bash
-H "Authorization: Bearer <token>"
-H "X-Auth-Provider: WORKOS"
```

Generate token:
```bash
uv run python token_generator.py --tenant app --env staging --role admin
```

---

## Known Issues & Workarounds

### 1. CreditDetail Model Bug (NOT part of warehouse settings)

**Location:** `commons/db/v6/commission/credits/credit_detail.py`

**Issue:** `product` and `uom` relationships defined without foreign key columns.

**Error:**
```
sqlalchemy.exc.ArgumentError: Mapper mapped class CreditDetail has no property 'product_id'
```

**Workaround:** Comment out the relationships in site-packages:
```python
# product: Mapped[Product | None] = relationship(...)
# uom: Mapped[ProductUom | None] = relationship(...)
```

**Status:** Needs to be fixed in flowbot-commons and published as new version.

### 2. Strawberry dict Type Not Supported

**Issue:** GraphQL/Strawberry doesn't support Python `dict` type directly.

**Fix:** Use `strawberry.scalars.JSON`:
```python
from strawberry.scalars import JSON

@strawberry.input
class ShippingCarrierInput:
    service_types: JSON | None = None  # NOT dict | None
```

### 3. HasCreatedBy Column Name

**Issue:** Migration used `created_by` but `HasCreatedBy` mixin creates `created_by_id`.

**Fix:** Use `created_by_id` in migration file.

---

## Testing Results

### Endpoints Tested: 20/25 Passed

| Category | Passed | Ready to Test |
|----------|--------|---------------|
| Container Types | 6/6 | - |
| Shipping Carriers | 6/6 | - |
| Warehouses | 8/13 | 5 (require user data) |

### Ready to Test (Need Valid User IDs)
- `assignWorkerToWarehouse`
- `updateWorkerRole`
- `removeWorkerFromWarehouse`
- `updateWarehouseSettings`
- `updateWarehouseStructure`

See [WAREHOUSE_SETTINGS_ENDPOINTS.md](WAREHOUSE_SETTINGS_ENDPOINTS.md) for full test details.

---

## Checklist for Future Sections

When building new settings sections, follow this checklist:

### 1. Models (flowbot-commons)

- [ ] Create model file in appropriate folder (`commons/db/v6/...`)
- [ ] Use correct base class (`PyWarehouseBaseModel` for warehouse-related)
- [ ] Add `__tablename__`
- [ ] Use correct column types (Text for long strings, JSONB for JSON data)
- [ ] Use `Decimal` for numeric fields (not `float`)
- [ ] Add to `__init__.py` exports
- [ ] Add to `models.py` exports

### 2. Migration (flow-py-backend)

- [ ] Create migration in `alembic/versions/`
- [ ] Use correct schema (`pywarehouse` for warehouse-related)
- [ ] Match column names exactly (e.g., `created_by_id` not `created_by`)
- [ ] Add foreign key constraints with appropriate `ON DELETE` behavior
- [ ] Include downgrade function

### 3. Backend Endpoints (flow-py-backend)

- [ ] Create folder structure: `mutations/`, `queries/`, `repositories/`, `services/`, `strawberry/`
- [ ] Strawberry input types: Use `JSON` for JSONB fields, not `dict`
- [ ] Strawberry response types: Match model field names (snake_case → camelCase happens automatically)
- [ ] Repository: Implement CRUD operations
- [ ] Service: Business logic layer
- [ ] Register in GraphQL schema

### 4. Testing

- [ ] Test all CRUD endpoints manually
- [ ] Verify list/get operations return correct data
- [ ] Verify create/update persist correctly
- [ ] Verify delete removes data
- [ ] Document test results

### 5. PR Process

- [ ] Commit to feature branch
- [ ] Push both repos (commons first if models changed)
- [ ] Create PR with clear description
- [ ] Address review feedback
- [ ] Update migration if schema changes requested
- [ ] Re-run migrations on test database after changes

---

## Commits Made

### flowbot-commons (feat/settings branch)
1. Initial warehouse models
2. `fix: move ContainerType and ShippingCarrier to pywarehouse schema`

### flow-py-backend (feat/settings branch)
1. Initial warehouse endpoints
2. `fix: warehouse settings migration and strawberry JSON type`
3. `fix: move container_types and shipping_carriers to pywarehouse schema`

---

## Contact

For questions about this implementation, refer to the PR discussions or the testing guide documentation.
