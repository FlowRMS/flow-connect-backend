# Field Map Virtual Defaults

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1569](https://linear.app/flow-labs/issue/FLO-1569/field-map-virtual-defaults)
- **Created**: 2026-02-04 23:46 -03
- **Approved**: 2026-02-04 23:57 -03
- **Finished**: 2026-02-05 09:12 -03
- **PR**: [#34](https://github.com/FlowRMS/flow-py-connect/pull/34)
- **Commit Prefix**: Field Map Virtual Defaults

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: Types Layer](#phase-1-types-layer)
- [Phase 2: Query Layer](#phase-2-query-layer)
- [Phase 3: Verification](#phase-3-verification)
- [GraphQL API Changes](#graphql-api-changes)
- [Review](#review)
- [Results](#results)

---

## Overview

Currently, the `fieldMap` GraphQL query returns `null` when no field map exists in the database for a given `(organization_id, map_type, direction)` combination. This requires users to call the `saveFieldMap` mutation before they can see any fields.

This plan implements **virtual defaults**: when no database record exists, the query returns a response constructed from the `DEFAULT_FIELDS` configuration with `id: null`, signaling "not yet persisted." The mutation continues to work as-is, creating the actual database record on first save.

**Benefits:**
- Query remains read-only (no side effects)
- No unnecessary database records for organizations that never customize
- Works for both global and organization-specific field maps
- Clear signal to frontend: `id === null` means "virtual defaults"

---

## Design Decisions

### DD-1: Virtual Defaults Over Auto-Create

**Decision**: Return in-memory defaults from config when no DB record exists, rather than auto-creating records.

- Query stays purely read-only (no database writes)
- Avoids creating records for organizations that never customize their field maps
- Default fields already defined in `field_map_config.py` - reuse them
- Mutation already handles record creation via `get_or_create_map()`

### DD-2: Nullable ID for Virtual Response

**Decision**: Return `id: null` for virtual field maps and their fields.

- Semantically correct - signals "not yet persisted"
- Frontend can detect virtual vs. persisted state
- No fake/sentinel IDs that could cause confusion
- Fields use `standard_field_key` as unique identifier (already exists)

---

## Critical Files

| File | Action | Description |
|------|--------|-------------|
| [`app/graphql/pos/field_map/strawberry/field_map_types.py`](../../app/graphql/pos/field_map/strawberry/field_map_types.py) | Modify ✅ | Make `id` nullable in responses, add `from_defaults()` factory |
| [`app/graphql/pos/field_map/queries/field_map_queries.py`](../../app/graphql/pos/field_map/queries/field_map_queries.py) | Modify ✅ | Return virtual defaults when DB record not found |
| [`tests/graphql/pos/field_map/test_field_map_types.py`](../../tests/graphql/pos/field_map/test_field_map_types.py) | Add ✅ | Tests for virtual defaults types |
| [`tests/graphql/pos/field_map/test_field_map_queries.py`](../../tests/graphql/pos/field_map/test_field_map_queries.py) | Add ✅ | Tests for query virtual defaults behavior |

---

## Phase 1: Types Layer

Update GraphQL response types to support virtual defaults.

### 1.1 RED: Write failing tests for nullable ID and from_defaults factory ✅

**File**: `tests/graphql/pos/field_map/test_field_map_types.py`

**Test scenarios**:
- `test_field_map_response_from_defaults_has_null_id` - Virtual response has `id=None`
- `test_field_map_response_from_defaults_has_all_default_fields` - Contains all 18 default fields
- `test_field_map_response_from_defaults_fields_have_null_id` - Each field has `id=None`
- `test_field_map_response_from_defaults_includes_categories` - Categories are populated
- `test_field_map_response_from_defaults_respects_map_type` - Correct `map_type` in response
- `test_field_map_response_from_defaults_respects_direction` - Correct `direction` in response
- `test_field_map_response_from_defaults_respects_organization_id` - Correct `organization_id` in response

### 1.2 GREEN: Implement nullable ID and from_defaults factory ✅

**File**: `app/graphql/pos/field_map/strawberry/field_map_types.py`

Changes:
- `FieldMapFieldResponse.id`: Change from `strawberry.ID` to `strawberry.ID | None`
- `FieldMapResponse.id`: Change from `strawberry.ID` to `strawberry.ID | None`
- Add `FieldMapFieldResponse.from_default_config()` static method - creates response from `DefaultFieldConfig`
- Add `FieldMapResponse.from_defaults()` static method - creates virtual response from `DEFAULT_FIELDS`

### 1.3 REFACTOR: Clean up implementation ✅

- Ensure type hints are complete
- No redundant code

### 1.4 VERIFY: Run `task all` ✅

---

## Phase 2: Query Layer

Update the query to return virtual defaults when no DB record exists.

### 2.1 RED: Write failing tests for query returning virtual defaults ✅

**File**: `tests/graphql/pos/field_map/test_field_map_queries.py`

**Test scenarios**:
- `test_field_map_query_returns_virtual_defaults_when_not_found` - Returns defaults with `id=null` when no DB record
- `test_field_map_query_returns_db_record_when_exists` - Returns actual record with real ID when exists
- `test_field_map_query_virtual_defaults_for_pot` - Works for POT map type
- `test_field_map_query_virtual_defaults_for_receive_direction` - Works for RECEIVE direction
- `test_field_map_query_virtual_defaults_with_organization_id` - Works with organization-specific queries

### 2.2 GREEN: Implement virtual defaults in query ✅

**File**: `app/graphql/pos/field_map/queries/field_map_queries.py`

Changes:
- When `repository.get_by_org_and_type()` returns `None`, call `FieldMapResponse.from_defaults()`
- Pass `organization_id`, `map_type`, and `direction` to factory method

### 2.3 REFACTOR: Clean up implementation ✅

- Ensure consistent return paths
- No redundant code

### 2.4 VERIFY: Run `task all` ✅

---

## Phase 3: Verification

Manual testing to verify the implementation works correctly.

### 3.1 Manual Testing ✅

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Query POS field map (no DB record) | Returns virtual defaults with `id: null` | ✅ (validated via POT - POS has existing DB record) |
| 2 | Query POT field map (no DB record) | Returns virtual defaults with `id: null` | ✅ |
| 3 | Query with RECEIVE direction (no DB record) | Returns virtual defaults | ✅ |
| 4 | Query existing POS field map | Returns actual record with real ID | ✅ |
| 5 | Save field map, then query | Returns persisted record with real ID | ✅ |
| 6 | Virtual response has all 18 default fields | Fields array has 18 items | ✅ |
| 7 | Virtual response has all 8 categories | Categories array has 8 items | ✅ |

---

## GraphQL API Changes

_Breaking and non-breaking changes to the GraphQL schema._

| Change | Type | Detail |
|--------|------|--------|
| `FieldMapResponse.id`: `ID!` → `ID` | ⚠️ Breaking | Nullable to support virtual defaults (DD-2) |
| `FieldMapFieldResponse.id`: `ID!` → `ID` | ⚠️ Breaking | Nullable to support virtual defaults (DD-2) |
| `fieldMap(...)`: `FieldMapResponse` → `FieldMapResponse!` | ✅ Non-breaking | Query always returns a response (never null) |

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns — virtual defaults built in-memory from config constants |
| 2 | Effects on other features | ✅ Schema changes are intentional (see note below) |
| 3 | Code quality issues | ✅ Clean — factory methods follow existing patterns |
| 4 | Potential bugs | ✅ None found — edge cases covered in 17 unit tests |
| 5 | Commit messages | ✅ Single-line, correct prefix format |
| 6 | No Co-Authored-By | ✅ None found |
| 7 | Breaking changes | ✅ Documented in GraphQL API Changes section |
| 8 | Document updates | ✅ No changes needed |

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 2 sessions (~2026-02-04 to 2026-02-05) |
| Phases | 3 |
| Files Modified | 9 |
| Tests Added | 17 |
