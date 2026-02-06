# Add Direction Field to FieldMap

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1392](https://linear.app/flow-labs/issue/FLO-1392/map-add-flag-to-know-if-is-send-or-receive)
- **Created**: 2026-01-30 15:41 -03
- **Approved**: 2026-01-30 16:10 -03
- **Finished**: 2026-01-30 20:19 -03
- **PR**: [#27](https://github.com/FlowRMS/flow-py-connect/pull/27)
- **Commit Prefix**: FieldMap Direction

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: Database Schema](#phase-1-database-schema)
- [Phase 2: Service Layer Updates](#phase-2-service-layer-updates)
- [Phase 3: GraphQL Layer](#phase-3-graphql-layer)
- [Phase 4: Validation Execution Integration](#phase-4-validation-execution-integration)
- [Phase 5: Verification](#phase-5-verification)
- [Results](#results)

---

## Overview

Add a `direction` field to `FieldMap` to distinguish between maps used for sending data vs receiving data.

**Current State:**
- FieldMap has `map_type` (POS/POT) and unique constraint `(organization_id, map_type)`
- Validation execution uses the map without direction context

**Proposed Change:**
- Add `direction` enum field: `SEND`, `RECEIVE`
- Update unique constraint to `(organization_id, map_type, direction)`
- Validation execution explicitly uses SEND maps
- RECEIVE maps reserved for future use

---

## Design Decisions

### DD-1: Direction as separate dimension (not replacing map_type)

**Decision**: Add `direction` as a new field alongside `map_type`.

- `map_type` defines WHAT is being mapped (POS data vs POT data)
- `direction` defines HOW it's used (sending out vs receiving in)
- This allows up to 4 maps per org: POS-SEND, POS-RECEIVE, POT-SEND, POT-RECEIVE
- Clean separation of concerns

### DD-2: Default value for backward compatibility

**Decision**: Default `direction` to `SEND`.

- Existing maps become SEND maps (current behavior preserved)
- Migration sets all existing records to SEND
- GraphQL query defaults to SEND if direction not specified

### DD-3: Updated unique constraint

**Decision**: Change unique constraint from `(organization_id, map_type)` to `(organization_id, map_type, direction)`.

- Allows separate SEND and RECEIVE maps per type
- Prevents duplicate maps for same org/type/direction combination

---

## Critical Files

| Type | File | Status |
|------|------|--------|
| Enum | [`app/graphql/pos/field_map/models/field_map_enums.py`](../../app/graphql/pos/field_map/models/field_map_enums.py) | ✅ |
| Model | [`app/graphql/pos/field_map/models/field_map.py`](../../app/graphql/pos/field_map/models/field_map.py) | ✅ |
| Migration | [`alembic/versions/20260130_add_field_map_direction.py`](../../alembic/versions/20260130_add_field_map_direction.py) | ✅ |
| Repository | [`app/graphql/pos/field_map/repositories/field_map_repository.py`](../../app/graphql/pos/field_map/repositories/field_map_repository.py) | ✅ |
| Service | [`app/graphql/pos/field_map/services/field_map_service.py`](../../app/graphql/pos/field_map/services/field_map_service.py) | ✅ |
| Types | [`app/graphql/pos/field_map/strawberry/field_map_types.py`](../../app/graphql/pos/field_map/strawberry/field_map_types.py) | ✅ |
| Query | [`app/graphql/pos/field_map/queries/field_map_queries.py`](../../app/graphql/pos/field_map/queries/field_map_queries.py) | ✅ |
| Mutation | [`app/graphql/pos/field_map/mutations/field_map_mutations.py`](../../app/graphql/pos/field_map/mutations/field_map_mutations.py) | ✅ |
| Service | [`app/graphql/pos/validations/services/validation_execution_service.py`](../../app/graphql/pos/validations/services/validation_execution_service.py) | ✅ |
| Test | [`tests/graphql/pos/field_map/test_field_map_repository.py`](../../tests/graphql/pos/field_map/test_field_map_repository.py) | ✅ |
| Test | [`tests/graphql/pos/field_map/test_field_map_service.py`](../../tests/graphql/pos/field_map/test_field_map_service.py) | ✅ |

---

## Phase 1: Database Schema

_Add direction enum and field to FieldMap model with migration._

### 1.1 GREEN: Add FieldMapDirection enum ✅

**File**: [`app/graphql/pos/field_map/models/field_map_enums.py`](../../app/graphql/pos/field_map/models/field_map_enums.py)

Add new enum:
- `FieldMapDirection` with values: `SEND`, `RECEIVE`

### 1.2 GREEN: Add direction field to FieldMap model ✅

**File**: [`app/graphql/pos/field_map/models/field_map.py`](../../app/graphql/pos/field_map/models/field_map.py)

**Schema Changes**:

| | **connect_pos.field_maps** | |
|-----|------|-------|
| **Column** | **Type** | **Constraints** |
| `direction` | `String(10)` | NOT NULL, DEFAULT `send` |
| | **Constraints** | |
| | `uq_field_maps_org_type_direction` | UNIQUE(`organization_id`, `map_type`, `direction`) - replaces existing `uq_field_maps_org_type` |

### 1.3 GREEN: Create migration ✅

**File**: [`alembic/versions/20260130_add_field_map_direction.py`](../../alembic/versions/20260130_add_field_map_direction.py)

Migration steps:
1. Add `direction` column with default `send`
2. Update existing records to have `direction = 'send'`
3. Drop old unique constraint `uq_field_maps_org_type`
4. Add new unique constraint `uq_field_maps_org_type_direction`

### 1.4 VERIFY: Run `task all` ✅

- Type checking: 0 errors ✅
- Lint: passes ✅
- field_map tests: 22 passed ✅
- Note: 1 pre-existing failing test on `main` (unrelated to this plan)

---

## Phase 2: Service Layer Updates

_Update repository and service to handle direction parameter._

### 2.1 RED: Write failing tests for repository with direction ✅

**File**: [`tests/graphql/pos/field_map/test_field_map_repository.py`](../../tests/graphql/pos/field_map/test_field_map_repository.py)

**Test scenarios**:
- `test_get_by_org_and_type_filters_by_direction` - Returns only maps matching direction
- `test_get_by_org_and_type_defaults_to_send` - Defaults to SEND when direction not specified

### 2.2 GREEN: Update FieldMapRepository ✅

**File**: [`app/graphql/pos/field_map/repositories/field_map_repository.py`](../../app/graphql/pos/field_map/repositories/field_map_repository.py)

- Add `direction` parameter to `get_by_org_and_type()` method
- Default to `FieldMapDirection.SEND` if not specified

### 2.3 RED: Write failing tests for service with direction ✅

**File**: [`tests/graphql/pos/field_map/test_field_map_service.py`](../../tests/graphql/pos/field_map/test_field_map_service.py)

**Test scenarios**:
- `test_get_or_create_with_direction` - Creates map with specified direction
- `test_save_preserves_direction` - Save operation respects direction field

### 2.4 GREEN: Update FieldMapService ✅

**File**: [`app/graphql/pos/field_map/services/field_map_service.py`](../../app/graphql/pos/field_map/services/field_map_service.py)

- Add `direction` parameter to `get_field_map()`, `get_or_create_map()`, `save_fields()` methods
- Pass direction through to repository calls

### 2.5 REFACTOR: Clean up, ensure type safety ✅

### 2.6 VERIFY: Run `task all` ✅

- Type checking: 0 errors ✅
- Lint: passes ✅
- field_map tests: 26 passed ✅

---

## Phase 3: GraphQL Layer

_Expose direction field in GraphQL types, queries, and mutations._

### 3.1 GREEN: Update response types ✅

**File**: [`app/graphql/pos/field_map/strawberry/field_map_types.py`](../../app/graphql/pos/field_map/strawberry/field_map_types.py)

- Added `FieldMapDirectionEnum` strawberry enum
- Added `direction: FieldMapDirection` to `FieldMapResponse`
- Added `direction: FieldMapDirection = SEND` to `SaveFieldMapInput`

### 3.2 GREEN: Update query with direction parameter ✅

**File**: [`app/graphql/pos/field_map/queries/field_map_queries.py`](../../app/graphql/pos/field_map/queries/field_map_queries.py)

- Added optional `direction: FieldMapDirection = SEND` parameter to `field_map` query
- Passes direction to repository call

### 3.3 GREEN: Update mutation input ✅

**File**: [`app/graphql/pos/field_map/mutations/field_map_mutations.py`](../../app/graphql/pos/field_map/mutations/field_map_mutations.py)

- Passes `direction` from input to service call

### 3.4 VERIFY: Run `task all` ✅

- Type checking: 0 errors ✅
- Lint: passes ✅
- field_map tests: 26 passed ✅

---

## Phase 4: Validation Execution Integration

_Update validation execution to explicitly use SEND maps._

### 4.1 RED: Write failing tests for SEND filtering ✅

**File**: [`tests/graphql/pos/validations/services/test_validation_execution_service.py`](../../tests/graphql/pos/validations/services/test_validation_execution_service.py)

**Test scenarios**:
- `test_validation_uses_send_direction_map` - Validation explicitly requests SEND maps

### 4.2 GREEN: Update ValidationExecutionService ✅

**File**: [`app/graphql/pos/validations/services/validation_execution_service.py`](../../app/graphql/pos/validations/services/validation_execution_service.py)

- Updated `_get_applicable_field_maps()` to explicitly pass `FieldMapDirection.SEND`

### 4.3 VERIFY: Run `task all` ✅

- Type checking: 0 errors ✅
- Lint: passes ✅
- validation_execution tests: 7 passed ✅

---

## Phase 5: Verification

_Manual testing and integration verification._

### 5.1 Test GraphQL query with direction parameter ✅

- Query field map with default direction (SEND) - returns existing map with `direction: "SEND"` ✅
- Query field map with `direction: RECEIVE` - returns `null` (no receive maps yet) ✅

### 5.2 Test schema introspection ✅

- `FieldMapDirection` enum exists with `SEND` and `RECEIVE` values ✅
- `FieldMapResponse.direction` field present ✅
- `fieldMap` query accepts `direction` parameter ✅
- `SaveFieldMapInput` accepts `direction` field ✅

### 5.3 Verify validation execution uses SEND maps ✅

- Covered by automated test `test_validation_uses_send_direction_map` ✅

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~4.5 hours |
| Phases | 5 |
| Files Modified | 14 |
| Tests Added | 5 |
