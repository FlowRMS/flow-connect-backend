# Field Mapping

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1160](https://linear.app/flow-labs/issue/FLO-1160/flowpos-field-mapping-and-permissions)
- **Created**: 2026-01-21 09:11 -03
- **Approved**: 2026-01-21 09:26 -03
- **Finished**: 2026-01-21 14:52 -03
- **PR**: [#12](https://github.com/FlowRMS/flow-py-connect/pull/12)
- **Commit Prefix**: Field Mapping

---

## Table of Contents

- [Summary](#summary)
- [Requirements](#requirements)
- [Technical Design](#technical-design)
- [Critical Files](#critical-files)
- [Phase 1: Database Schema](#phase-1-database-schema)
- [Phase 2: Repository Layer](#phase-2-repository-layer)
- [Phase 3: Service Layer](#phase-3-service-layer)
- [Phase 4: GraphQL Layer](#phase-4-graphql-layer)
- [Phase 5: Verification](#phase-5-verification)
- [Results](#results)

---

## Summary

Implement a Field Mapping feature for the POS domain that allows users to configure how their data fields map to standard Flow fields. The system supports:
- Two map types: POS (Point of Sale) and POT (Point of Transfer)
- Default maps (organization_id = null) and organization-specific maps
- Fixed categories with metadata (Name, Description, Order, Visible)
- Default fields that are auto-populated when creating a new map
- User-defined custom fields (non-default)

---

## Requirements

### Map Structure
- A map is identified by `(organization_id, map_type)` - only one map per combination
- `organization_id` can be null for default maps
- `map_type` is either POS or POT

### Categories
Fixed list of categories (all tenants share the same list):

| Order | Name | Description |
|-------|------|-------------|
| 1 | Transaction | Transaction-level information |
| 2 | Selling Branch (Credit Owner) | Selling branch details |
| 3 | Territory (ZIP Codes) | Geographic territory info |
| 4 | Shipping Branch (Fulfillment) | Shipping/fulfillment location |
| 5 | Bill-To (Billing Context) | Billing entity information |
| 6 | Product Identification | Product identifiers |
| 7 | Quantity & Pricing | Quantity and pricing data |
| 8 | Custom Columns | User-defined custom fields |

### Field Attributes

| Attribute | Type | Editable | Notes |
|-----------|------|----------|-------|
| standard_field_name | text | Only if is_default=false | Mandatory |
| standard_field_name_description | text | No | Only for default fields |
| organization_field_name | text | Yes | User's mapped field |
| status | enum | No | Required, Optional, Highly Suggested, One Required, Can Calculate |
| manufacturer | bool | Yes | Mandatory when linked=true |
| rep | bool | Yes | Mandatory when linked=true |
| linked | bool | No | Auto-calculated from organization_field_name |
| preferred | bool | No | Default false |
| is_default | bool | No | Default false for user-added fields |
| field_type | enum | Only if is_default=false | Text, Date, Decimal, Integer |

### Default Fields

17 default fields across categories (see specification for full list):
- Transaction: Transaction Date, Order Type
- Selling Branch: Selling Branch #, Selling Branch Name / City
- Territory: Selling Branch Zip Code
- Shipping Branch: Shipping Branch #, Shipping Branch Name / City, Shipping Branch Zip Code
- Bill-To: Bill-To Account / Code, Bill-To Branch Name / City, Bill-To Branch Zip Code
- Product Identification: Manufacturer Catalog #, Manufacturer SKU #, UPC Code, Unit of Measure
- Quantity & Pricing: Quantity (# of Units Sold), Distributor Unit Cost, Extended Net Price

### User Operations
- Add new fields (non-default only)
- Edit fields:
  - Default fields: can edit organization_field_name, manufacturer, rep
  - Custom fields: can also edit standard_field_name, field_type
- Delete fields (non-default only)

---

## Technical Design

### Enums

```
FieldMapType: POS, POT
FieldStatus: REQUIRED, OPTIONAL, HIGHLY_SUGGESTED, ONE_REQUIRED, CAN_CALCULATE
FieldType: TEXT, DATE, DECIMAL, INTEGER
FieldCategory: TRANSACTION, SELLING_BRANCH, TERRITORY, SHIPPING_BRANCH, BILL_TO, PRODUCT_IDENTIFICATION, QUANTITY_PRICING, CUSTOM_COLUMNS
```

### Category Configuration

Use a config pattern (similar to user_preferences) to store category metadata:
```python
CATEGORY_CONFIG = {
    FieldCategory.TRANSACTION: CategoryConfig(name="Transaction", description="...", order=1, visible=True),
    ...
}
```

### Default Fields Configuration

Define default fields in configuration (not database seeding):
```python
DEFAULT_FIELDS = [
    DefaultFieldConfig(
        key="transaction_date",
        category=FieldCategory.TRANSACTION,
        standard_field_name="Transaction Date",
        description="The date of the transaction or invoice.",
        status=FieldStatus.REQUIRED,
        field_type=FieldType.DATE,
        preferred=False,
    ),
    ...
]
```

Key generation for custom fields: `generate_unique_field_key(name, existing_keys)` - Slugifies name and adds numeric suffix on collision.

### Database Models

**FieldMap**: Main map entity
- `id`: UUID (PK)
- `organization_id`: UUID | None (nullable for default)
- `map_type`: FieldMapType
- Unique constraint: `(organization_id, map_type)`

**FieldMapField**: Fields within a map
- `id`: UUID (PK)
- `field_map_id`: UUID (FK to FieldMap)
- `standard_field_key`: str (natural key for field identification)
- `category`: FieldCategory
- `standard_field_name`: str
- `standard_field_name_description`: str | None
- `organization_field_name`: str | None
- `status`: FieldStatus
- `manufacturer`: bool | None
- `rep`: bool | None
- `linked`: bool
- `preferred`: bool
- `is_default`: bool
- `field_type`: FieldType
- `display_order`: int (for display ordering within category)
- Unique constraint: `(field_map_id, standard_field_key)`

### GraphQL Operations

**Query**: `fieldMap(organizationId: ID, mapType: FieldMapType!) -> FieldMapResponse | null`

**Mutation**: `saveFieldMap(input: SaveFieldMapInput!) -> FieldMapResponse`
- Creates map if doesn't exist (populates with default fields)
- Updates existing map fields

---

## Critical Files

| File | Purpose | Status |
|------|---------|--------|
| [`app/graphql/pos/field_map/models/field_map_enums.py`](../../app/graphql/pos/field_map/models/field_map_enums.py) | Enums for field mapping | ✅ |
| [`app/graphql/pos/field_map/models/field_map_config.py`](../../app/graphql/pos/field_map/models/field_map_config.py) | Category and default fields config | ✅ |
| [`app/graphql/pos/field_map/models/field_map.py`](../../app/graphql/pos/field_map/models/field_map.py) | FieldMap and FieldMapField models | ✅ |
| [`alembic/versions/20260121_create_field_maps.py`](../../alembic/versions/20260121_create_field_maps.py) | Migration | ✅ |
| [`app/graphql/pos/field_map/repositories/field_map_repository.py`](../../app/graphql/pos/field_map/repositories/field_map_repository.py) | Repository | ✅ |
| [`app/graphql/pos/field_map/exceptions.py`](../../app/graphql/pos/field_map/exceptions.py) | Custom exceptions | ✅ |
| [`app/graphql/pos/field_map/services/field_map_service.py`](../../app/graphql/pos/field_map/services/field_map_service.py) | Service | ✅ |
| [`app/graphql/pos/field_map/strawberry/field_map_types.py`](../../app/graphql/pos/field_map/strawberry/field_map_types.py) | GraphQL types | ✅ |
| [`app/graphql/pos/field_map/queries/field_map_queries.py`](../../app/graphql/pos/field_map/queries/field_map_queries.py) | GraphQL query | ✅ |
| [`app/graphql/pos/field_map/mutations/field_map_mutations.py`](../../app/graphql/pos/field_map/mutations/field_map_mutations.py) | GraphQL mutation | ✅ |
| [`tests/graphql/pos/field_map/test_field_map_repository.py`](../../tests/graphql/pos/field_map/test_field_map_repository.py) | Repository tests | ✅ |
| [`tests/graphql/pos/field_map/test_field_map_service.py`](../../tests/graphql/pos/field_map/test_field_map_service.py) | Service tests | ✅ |

---

## Phase 1: Database Schema

Define models, enums, configuration, and create migration.

### 1.1 GREEN: Create enums ✅
**File**: [`app/graphql/pos/field_map/models/field_map_enums.py`](../../app/graphql/pos/field_map/models/field_map_enums.py)
- Define `FieldMapType`, `FieldStatus`, `FieldType`, `FieldCategory` enums using StrEnum

### 1.2 GREEN: Create configuration ✅
**File**: [`app/graphql/pos/field_map/models/field_map_config.py`](../../app/graphql/pos/field_map/models/field_map_config.py)
- Define `CategoryConfig` dataclass with: name, description, order, visible
- Define `DefaultFieldConfig` dataclass with: category, standard_field_name, description, status, field_type, preferred
- Create `CATEGORY_CONFIG` dictionary
- Create `DEFAULT_FIELDS` list with all 17 default fields
- Add helper functions: `get_category_config()`, `get_default_fields()`

### 1.3 GREEN: Create FieldMap model ✅
**File**: [`app/graphql/pos/field_map/models/field_map.py`](../../app/graphql/pos/field_map/models/field_map.py)
- Extends `PyConnectPosBaseModel`, `HasCreatedBy`, `HasCreatedAt`
- Fields: id, organization_id (nullable), map_type
- Unique constraint on (organization_id, map_type)
- Relationship to FieldMapField

### 1.4 GREEN: Create FieldMapField model ✅
**File**: [`app/graphql/pos/field_map/models/field_map.py`](../../app/graphql/pos/field_map/models/field_map.py) (merged with FieldMap)
- Extends `PyConnectPosBaseModel`
- All field attributes as defined in requirements
- Foreign key to FieldMap

### 1.5 GREEN: Create migration ✅
**File**: [`alembic/versions/20260121_create_field_maps.py`](../../alembic/versions/20260121_create_field_maps.py)
- Create `field_maps` table
- Create `field_map_fields` table
- Add indexes for common queries

### 1.6 VERIFY: Run checks ✅
- Run `task all` to verify types and lint pass

### Opportunistic Refactor: POS Domain Structure ✅

While creating the field_map package, we identified that the POS domain needed better organization. Refactored to split features into separate packages:

**Before:**
```
app/graphql/pos/
├── models/
├── repositories/
├── services/
├── mutations/
└── strawberry/
```

**After:**
```
app/graphql/pos/
├── agreement/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── mutations/
│   └── strawberry/
└── field_map/
    ├── models/
    ├── repositories/
    ├── services/
    ├── mutations/
    ├── queries/
    └── strawberry/
```

**Files moved/updated:**
- Moved all agreement files to `pos/agreement/`
- Moved all field_map files to `pos/field_map/`
- Updated imports in: `schema.py`, `organization_types.py`, `manufacturer_service.py`, tests
- Extracted `_setup_s3_delete_mock` helper in `test_agreement_service.py` (removed duplication)

---

## Phase 2: Repository Layer

Implement data access layer with TDD.

### 2.1 RED: Write repository tests ✅
**File**: [`tests/graphql/pos/field_map/test_field_map_repository.py`](../../tests/graphql/pos/field_map/test_field_map_repository.py)

**Test scenarios** (11 tests):
- `test_create_field_map_success` - Creates a new field map
- `test_get_by_org_and_type_found` - Returns map when exists
- `test_get_by_org_and_type_not_found` - Returns None when not exists
- `test_get_by_org_and_type_with_null_org` - Works with null organization_id (default map)
- `test_add_field_to_map` - Adds a field to existing map
- `test_add_fields_bulk` - Adds multiple fields in bulk
- `test_update_field` - Updates field attributes
- `test_delete_field` - Removes field from map
- `test_delete_field_not_found` - Returns False when field doesn't exist
- `test_get_field_by_id_found` - Returns field when found
- `test_get_field_by_id_not_found` - Returns None when field doesn't exist

### 2.2 GREEN: Implement repository ✅
**File**: [`app/graphql/pos/field_map/repositories/field_map_repository.py`](../../app/graphql/pos/field_map/repositories/field_map_repository.py)

Methods:
- `create(field_map: FieldMap) -> FieldMap`
- `get_by_org_and_type(org_id: UUID | None, map_type: FieldMapType) -> FieldMap | None`
- `add_field(field: FieldMapField) -> FieldMapField`
- `add_fields(fields: list[FieldMapField]) -> list[FieldMapField]`
- `update_field(field: FieldMapField) -> FieldMapField`
- `delete_field(field_id: UUID) -> bool`
- `get_field_by_id(field_id: UUID) -> FieldMapField | None`

### 2.3 REFACTOR: Clean up ✅
- No refactoring needed - code is clean and type-safe

### 2.4 VERIFY: Run checks ✅
- All 101 tests pass
- Type checks pass
- Lint passes

---

## Phase 3: Service Layer

Implement business logic with TDD.

### 3.1 RED: Write service tests ✅
**File**: [`tests/graphql/pos/field_map/test_field_map_service.py`](../../tests/graphql/pos/field_map/test_field_map_service.py)

**Test scenarios** (13 tests):
- `test_get_or_create_map_creates_new_with_defaults` - Creates map with default fields when not exists
- `test_get_or_create_map_returns_existing` - Returns existing map without modification
- `test_update_field_updates_attributes` - Updates field attributes
- `test_add_custom_field_success` - Adds non-default field
- `test_delete_custom_field_success` - Removes non-default field
- `test_cannot_delete_default_field` - Raises error when deleting default field
- `test_cannot_edit_standard_name_of_default_field` - Raises error on invalid edit
- `test_cannot_edit_field_type_of_default_field` - Raises error when editing field_type of default
- `test_linked_auto_calculated_when_org_field_set` - linked=True when organization_field_name is set
- `test_linked_false_when_org_field_cleared` - linked=False when organization_field_name is cleared
- `test_manufacturer_rep_required_when_linked` - Validates manufacturer/rep when linked
- `test_delete_field_not_found` - Raises error when field not found
- `test_update_field_not_found` - Raises error when field not found for update

### 3.2 GREEN: Implement service ✅
**File**: [`app/graphql/pos/field_map/services/field_map_service.py`](../../app/graphql/pos/field_map/services/field_map_service.py)

**Exceptions File**: [`app/graphql/pos/field_map/exceptions.py`](../../app/graphql/pos/field_map/exceptions.py)

Methods:
- `get_or_create_map(org_id: UUID | None, map_type: FieldMapType) -> FieldMap`
- `add_custom_field(field_map_id: UUID, category, standard_field_name, field_type) -> FieldMapField`
- `update_field(field_id: UUID, **kwargs) -> FieldMapField`
- `delete_field(field_id: UUID) -> None`

Private helpers:
- `_create_default_fields(field_map_id: UUID) -> list[FieldMapField]`
- `_calculate_linked(organization_field_name: str | None) -> bool`
- `_validate_field_update(field, standard_field_name, field_type) -> None`

### 3.3 REFACTOR: Clean up ✅
- Code already clean - no refactoring needed

### 3.4 VERIFY: Run checks ✅
- All 114 tests pass
- Type checks pass
- Lint passes

---

## Phase 4: GraphQL Layer

Implement types, query, and mutation with declarative API design.

### Design: Declarative Field Input

The mutation uses a declarative approach - frontend sends the desired state, backend reconciles:

```graphql
input SaveFieldMapInput {
  organizationId: ID
  mapType: FieldMapType!
  fields: [FieldInput!]!
}
```

**Key design decisions:**
- **`standard_field_key`** - Natural key for field identification within a map
- **Default fields** have predefined keys (e.g., `transaction_date`, `order_type`)
- **Custom fields** auto-generate keys from slugified names with collision handling
- **Backend reconciliation** - Compares incoming fields with existing, determines adds/updates/deletes
- **Unique constraint** on `(field_map_id, standard_field_key)`

### 4.1 GREEN: Add standard_field_key to model ✅
**File**: [`app/graphql/pos/field_map/models/field_map.py`](../../app/graphql/pos/field_map/models/field_map.py)
- Added `standard_field_key: Mapped[str]` column
- Added unique constraint `uq_field_map_fields_map_key` on `(field_map_id, standard_field_key)`

### 4.2 GREEN: Add keys to DefaultFieldConfig ✅
**File**: [`app/graphql/pos/field_map/models/field_map_config.py`](../../app/graphql/pos/field_map/models/field_map_config.py)
- Added `key` field to `DefaultFieldConfig` dataclass
- Added predefined keys for all 17 default fields
- Added `generate_field_key()` - Slugifies name to create key
- Added `generate_unique_field_key()` - Handles collision with numeric suffix
- Added `DEFAULT_FIELD_KEYS` set for quick lookup

### 4.3 GREEN: Update migration ✅
**File**: [`alembic/versions/20260121_create_field_maps.py`](../../alembic/versions/20260121_create_field_maps.py)
- Added `standard_field_key` column
- Added unique constraint

### 4.4 GREEN: Update service with reconciliation ✅
**File**: [`app/graphql/pos/field_map/services/field_map_service.py`](../../app/graphql/pos/field_map/services/field_map_service.py)
- Added `FieldInput` dataclass for service layer
- Added `save_fields()` method with declarative reconciliation:
  - Builds lookup of existing fields by key
  - Processes incoming fields (update existing or add new)
  - Deletes fields not in incoming list (custom only, raises for default)

### 4.5 GREEN: Create GraphQL types ✅
**File**: [`app/graphql/pos/field_map/strawberry/field_map_types.py`](../../app/graphql/pos/field_map/strawberry/field_map_types.py)

Types:
- `FieldMapTypeEnum`, `FieldStatusEnum`, `FieldTypeEnum`, `FieldCategoryEnum` - Strawberry enums
- `CategoryConfigResponse` - Category metadata
- `FieldMapFieldResponse` - Field DTO with `standard_field_key`
- `FieldMapResponse` - Map with fields and category configs
- `FieldInput` - Unified input for default and custom fields
- `SaveFieldMapInput` - Declarative mutation input

### 4.6 GREEN: Create query ✅
**File**: [`app/graphql/pos/field_map/queries/field_map_queries.py`](../../app/graphql/pos/field_map/queries/field_map_queries.py)

Query:
- `field_map(organization_id: ID | None, map_type: FieldMapType!) -> FieldMapResponse | None`

### 4.7 GREEN: Create mutation ✅
**File**: [`app/graphql/pos/field_map/mutations/field_map_mutations.py`](../../app/graphql/pos/field_map/mutations/field_map_mutations.py)

Mutation:
- `save_field_map(input: SaveFieldMapInput!) -> FieldMapResponse`
- Converts GraphQL input to service input
- Calls `service.save_fields()` for declarative reconciliation

### 4.8 GREEN: Register in schema ✅
**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)
- Added `FieldMapQueries` to Query class
- Added `FieldMapMutations` to Mutation class

### 4.9 GREEN: Update tests ✅
**Files**:
- [`tests/graphql/pos/field_map/test_field_map_repository.py`](../../tests/graphql/pos/field_map/test_field_map_repository.py) - Updated with `standard_field_key`
- [`tests/graphql/pos/field_map/test_field_map_service.py`](../../tests/graphql/pos/field_map/test_field_map_service.py) - Rewrote for declarative API (11 tests)

### 4.10 VERIFY: Run checks ✅
- All 112 tests pass
- Type checks pass
- Lint passes
- GraphQL schema exported successfully

---

## Phase 5: Verification

Manual testing and final verification.

### 5.1 Manual Testing ✅
Tested via curl against local server (port 8010):

- ✅ Query field map (returns null initially)
- ✅ Save field map (creates with 17 default fields)
- ✅ Query field map (returns populated map)
- ✅ Update field mapping (organizationFieldName, linked auto-calculated)
- ✅ Add custom field (standardFieldName, fieldType, category required)
- ✅ Delete custom field (by omitting from fields array)

### 5.2 Validation Errors ✅
- ✅ Cannot delete default field - `CannotDeleteDefaultFieldError`
- ✅ manufacturer/rep required when linked - `LinkedFieldValidationError`

---

## Changes During Testing

### Bug Fix: Lazy Loading in Async Context

**Problem**: `greenlet_spawn has not been called` error when saving field map.

**Cause**: After creating a map with `repository.create()` and adding default fields with `repository.add_fields()`, the returned `created_map` object didn't have its `fields` relationship loaded. Accessing `field_map.fields` attempted lazy loading in an async context.

**Solution**: Re-fetch the map after creation to load fields via `joinedload`.

**Files Modified**:
- [`app/graphql/pos/field_map/services/field_map_service.py`](../../app/graphql/pos/field_map/services/field_map_service.py) - Re-fetch map after creation
- [`tests/graphql/pos/field_map/test_field_map_service.py`](../../tests/graphql/pos/field_map/test_field_map_service.py) - Updated test mock

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~5.5 hours |
| Phases | 5 |
| Files Changed | 39 (+2,423 / -38) |
| Tests Added | 22 |