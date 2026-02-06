# Distributor Search Query

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1267](https://linear.app/flow-labs/issue/FLO-1267/flowpos-distributors-list)
- **Created**: 2026-01-23 16:03 -03
- **Approved**: 2026-01-23 16:08 -03
- **Finished**: 2026-01-26
- **PR**: [#19](https://github.com/FlowRMS/flow-py-connect/pull/19)
- **Commit Prefix**: Distributor Search

---

## Table of Contents

- [Overview](#overview)
- [DRY Strategy](#dry-strategy)
- [Critical Files](#critical-files)
- [Phase 1: Repository Refactoring](#phase-1-repository-refactoring)
- [Phase 2: Distributor Service & Query](#phase-2-distributor-service--query)
- [Phase 3: Verification](#phase-3-verification)
- [Results](#results)

---

## Overview

Add a new `distributorSearch` GraphQL query that mirrors the existing `manufacturerSearch` functionality but filters by `org_type = "distributor"` instead of `"manufacturer"`.

The current `manufacturerSearch` implementation:
- **Repository**: `ManufacturerRepository.search()` - hardcodes `OrgType.MANUFACTURER` filter
- **Service**: `ManufacturerService.search()` - orchestrates search with POS contacts, agreements
- **Resolver**: `ManufacturerQueries.manufacturer_search()` - GraphQL query endpoint

---

## DRY Strategy

**Design Pattern**: Strategy Pattern (GoF)

Instead of duplicating the entire stack, we:

1. **Create `OrganizationSearchRepository`** with `org_type` parameter for all search operations
2. **Delete `ManufacturerRepository`** - services use `OrganizationSearchRepository` directly
3. **Update existing services** to use `OrganizationSearchRepository` with their respective `OrgType`
4. **Create `DistributorService`** that uses `OrganizationSearchRepository` with `OrgType.DISTRIBUTOR`
5. **Create `DistributorQueries`** with the new GraphQL query

This achieves maximum code reuse with minimal indirection.

---

## Critical Files

| File | Action | Description |
|------|--------|-------------|
| [`app/graphql/organizations/repositories/organization_search_repository.py`](../../app/graphql/organizations/repositories/organization_search_repository.py) | ✅ Create | Generic search with org_type parameter |
| [`app/graphql/organizations/repositories/__init__.py`](../../app/graphql/organizations/repositories/__init__.py) | ✅ Modify | Export OrganizationSearchRepository |
| `app/graphql/organizations/repositories/manufacturer_repository.py` | ✅ Delete | Replaced by OrganizationSearchRepository |
| [`app/graphql/organizations/services/organization_search_service.py`](../../app/graphql/organizations/services/organization_search_service.py) | ✅ Create | Generic search service with org_type parameter |
| [`app/graphql/organizations/services/organization_search_result.py`](../../app/graphql/organizations/services/organization_search_result.py) | ✅ Create | Generic search result dataclass |
| [`app/graphql/organizations/services/manufacturer_creation_service.py`](../../app/graphql/organizations/services/manufacturer_creation_service.py) | ✅ Modify | Use OrganizationSearchRepository |
| [`app/graphql/organizations/services/__init__.py`](../../app/graphql/organizations/services/__init__.py) | ✅ Modify | Export OrganizationSearchService |
| `app/graphql/organizations/services/manufacturer_service.py` | ✅ Delete | Replaced by OrganizationSearchService |
| `app/graphql/organizations/services/distributor_service.py` | ✅ Delete | Replaced by OrganizationSearchService |
| `app/graphql/organizations/queries/manufacturer_queries.py` | ✅ Delete | Replaced by ConnectionQueries |
| `app/graphql/organizations/queries/distributor_queries.py` | ✅ Delete | Replaced by ConnectionQueries |
| [`app/graphql/organizations/queries/connection_queries.py`](../../app/graphql/organizations/queries/connection_queries.py) | ✅ Create | Single `connectionSearch` query |
| [`app/graphql/organizations/queries/__init__.py`](../../app/graphql/organizations/queries/__init__.py) | ✅ Modify | Export ConnectionQueries |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | ✅ Modify | Add ConnectionQueries to schema |
| [`tests/graphql/organizations/test_organization_search_repository.py`](../../tests/graphql/organizations/test_organization_search_repository.py) | ✅ Create | Tests for generic repository |
| [`tests/graphql/organizations/test_organization_search_service.py`](../../tests/graphql/organizations/test_organization_search_service.py) | ✅ Create | Tests for generic service |
| `tests/graphql/organizations/test_manufacturer_repository.py` | ✅ Delete | Replaced by test_organization_search_repository |
| `tests/graphql/organizations/test_manufacturer_service.py` | ✅ Delete | Replaced by test_organization_search_service |

---

## Phase 1: Repository Refactoring ✅

Create `OrganizationSearchRepository` as the single repository for all organization search/lookup operations. Delete `ManufacturerRepository` and update services to use the new repository directly.

### 1.1 RED: Write failing tests for OrganizationSearchRepository ✅

**File**: [`tests/graphql/organizations/test_organization_search_repository.py`](../../tests/graphql/organizations/test_organization_search_repository.py)

**Test scenarios**:
- `test_search_filters_by_manufacturer_type` - Verifies OrgType.MANUFACTURER filter works
- `test_search_filters_by_distributor_type` - Verifies OrgType.DISTRIBUTOR filter works
- `test_search_different_types_produce_different_queries` - Verifies different types produce different SQL

### 1.2 GREEN: Implement OrganizationSearchRepository ✅

**File**: [`app/graphql/organizations/repositories/organization_search_repository.py`](../../app/graphql/organizations/repositories/organization_search_repository.py)

Methods:
- `search(org_type, ...)` - Generic search with org_type parameter
- `get_by_id(org_id)` - Fetch organization by ID
- `get_by_domain(domain, org_type)` - Fetch organization by domain and type

### 1.3 REFACTOR: Delete ManufacturerRepository, update services ✅

**Changes**:
- Deleted `app/graphql/organizations/repositories/manufacturer_repository.py`
- Updated `ManufacturerService` to use `OrganizationSearchRepository` directly
- Updated `ManufacturerCreationService` to use `OrganizationSearchRepository` directly
- Updated exports in `__init__.py` files
- Updated all related tests

### 1.4 REFACTOR: Extract OrganizationSearchResult dataclass ✅

**File**: [`app/graphql/organizations/services/organization_search_result.py`](../../app/graphql/organizations/services/organization_search_result.py)

- Extracted `ManufacturerSearchResult` into generic `OrganizationSearchResult`
- Updated `ManufacturerService` to use `OrganizationSearchResult`
- Updated exports in `services/__init__.py`

### 1.5 VERIFY: Run `task all` ✅

---

## Phase 2: Distributor Service & Query ✅

Create the distributor-specific service and GraphQL query.

### 2.1 RED: Write failing tests for DistributorService ✅

**File**: [`tests/graphql/organizations/test_distributor_service.py`](../../tests/graphql/organizations/test_distributor_service.py)

**Test scenarios**:
- `test_search_passes_distributor_org_type` - Verifies OrgType.DISTRIBUTOR is passed
- `test_search_returns_empty_list_when_no_results` - Verifies empty list returned
- `test_search_includes_pos_contacts` - Verifies POS contacts are fetched

### 2.2 GREEN: Implement DistributorService and DistributorQueries ✅

**Files**:
- [`app/graphql/organizations/services/distributor_service.py`](../../app/graphql/organizations/services/distributor_service.py) - Distributor search service
- [`app/graphql/organizations/queries/distributor_queries.py`](../../app/graphql/organizations/queries/distributor_queries.py) - GraphQL query

**DistributorService**:
- Uses `OrganizationSearchRepository.search(org_type=OrgType.DISTRIBUTOR)`
- Same orchestration logic as ManufacturerService (POS contacts, agreements)

**DistributorQueries**:
- `distributor_search()` query with same parameters as `manufacturer_search()`
- Returns `list[OrganizationLiteResponse]`

### 2.3 REFACTOR: Update exports and integrate into schema ✅

**Files**:
- [`app/graphql/organizations/services/__init__.py`](../../app/graphql/organizations/services/__init__.py) - Export DistributorService
- [`app/graphql/organizations/queries/__init__.py`](../../app/graphql/organizations/queries/__init__.py) - Export DistributorQueries
- [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) - Add DistributorQueries to Query type

### 2.4 VERIFY: Run `task all` ✅

### 2.5 REFACTOR: Consolidate services into single OrganizationSearchService ✅

**Problem**: `ManufacturerService` and `DistributorService` were nearly identical (only `OrgType` differed).

**Solution**: Created single `OrganizationSearchService` with `org_type` as search parameter.

**Changes**:
- Created [`app/graphql/organizations/services/organization_search_service.py`](../../app/graphql/organizations/services/organization_search_service.py)
- Deleted `manufacturer_service.py` and `distributor_service.py`
- Updated both queries to use `OrganizationSearchService`
- Consolidated tests into [`tests/graphql/organizations/test_organization_search_service.py`](../../tests/graphql/organizations/test_organization_search_service.py)

### 2.6 VERIFY: Run `task all` ✅

### 2.7 REFACTOR: Consolidate queries into single `connectionSearch` ✅

**Problem**: `ManufacturerQueries` and `DistributorQueries` are nearly identical. Additionally, the frontend shouldn't need to know which org type to search - the backend can infer this from the user's organization.

**Business Rule**: Manufacturers search for distributors, distributors search for manufacturers (complementary relationship for connections).

**Solution**: Create single `connectionSearch` query that:
1. Gets user's organization type
2. Searches for the opposite org type automatically
3. Replaces both `manufacturerSearch` and `distributorSearch`

**Design Pattern**: Template Method Pattern (GoF) - the algorithm structure is fixed (get user org → determine target type → search), but the target org type varies based on user context.

**Changes**:
- Added `search_for_connections()` method to `OrganizationSearchService`
- Created [`app/graphql/organizations/queries/connection_queries.py`](../../app/graphql/organizations/queries/connection_queries.py) with `connection_search()` query
- Deleted `ManufacturerQueries` and `DistributorQueries`
- Updated schema to use `ConnectionQueries`
- Added tests for `search_for_connections()` in `test_organization_search_service.py`

### 2.8 VERIFY: Run `task all` ✅

---

## Phase 3: Verification ✅

Manual testing of the new GraphQL query.

### 3.1 Test connectionSearch query ✅

- ✅ Basic search returns organizations with all expected fields
- ✅ `active: true` returns active organizations (default)
- ✅ `active: false` returns inactive organizations
- ✅ `active: null` returns both active and inactive
- ✅ `flowConnectMember: true` filters to members only (empty in test data)
- ✅ `flowConnectMember: false` filters to non-members only
- ✅ `connected: true` returns organizations with connections (ACCEPTED, DRAFT)
- ✅ `connected: false` returns organizations without connections
- ✅ `limit` parameter works correctly
- ✅ Response includes `posContacts` and `connectionStatus`

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 2026-01-23 to 2026-01-26 (3 days) |
| Phases | 3 |
| Files Modified | 16 (6 created, 7 modified, 5 deleted) |
| Tests Added | 2 test files |