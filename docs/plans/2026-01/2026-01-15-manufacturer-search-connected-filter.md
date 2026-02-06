# Manufacturer Search Connected Filter

- **Status**: ✅ Complete
- **Created**: 2026-01-15 13:01 -03
- **Approved**: 2026-01-15 13:29 -03
- **Finished**: 2026-01-15 15:45 -03
- **Commit Prefix**: Manufacturer Search Changes

## Table of Contents

- [Summary](#summary)
- [Changes Overview](#changes-overview)
- [Critical Files](#critical-files)
- [Phase 1: Repository Layer - Active Filter](#phase-1-repository-layer---active-filter-)
- [Phase 2: Repository Layer - Connected Filter](#phase-2-repository-layer---connected-filter-)
- [Phase 3: Service Layer Updates](#phase-3-service-layer-updates-)
- [Phase 4: GraphQL Layer](#phase-4-graphql-layer-)
- [Phase 5: Verification](#phase-5-verification-)

---

## Summary

Two changes to `manufacturerSearch`:

1. **`active` filter**: Change from `Boolean! = true` to `Boolean = true` (make nullable)
   - `active=True` → active orgs (default)
   - `active=False` → inactive orgs
   - `active=null` → all orgs

2. **`connected` filter**: Add new nullable boolean filter with default `null`
   - `connected=True` → only orgs connected to current user's org
   - `connected=False` → only orgs NOT connected
   - `connected=null` → all orgs (default)

Both filters implemented at **repository level** using subqueries (same pattern as `flow_connect_member`).

---

## Changes Overview

| Filter | Current Type | Current Default | New Type | New Default |
|--------|--------------|-----------------|----------|-------------|
| `active` | `Boolean!` | `true` | `Boolean` | `true` |
| `connected` | N/A | N/A | `Boolean` | `null` |

**Architecture change**: `connected` status moves from service-level computation to repository-level subquery.

| Aspect | Before | After |
|--------|--------|-------|
| Queries | 2 (orgs + connections) | 1 (with subquery) |
| Return type | `tuple[RemoteOrg, bool]` | `tuple[RemoteOrg, bool, bool]` |
| Connected computation | Service layer | Repository subquery |

---

## Critical Files

| File | Action | Status |
|------|--------|--------|
| [`app/graphql/organizations/repositories/manufacturer_repository.py`](../../app/graphql/organizations/repositories/manufacturer_repository.py) | Modify | ✅ |
| [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py) | Modify | ✅ |
| [`app/graphql/organizations/queries/manufacturer_queries.py`](../../app/graphql/organizations/queries/manufacturer_queries.py) | Modify | ✅ |
| [`tests/graphql/organizations/test_manufacturer_repository.py`](../../tests/graphql/organizations/test_manufacturer_repository.py) | Create | ✅ |
| [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py) | Modify | ✅ |

---

## Phase 1: Repository Layer - Active Filter ✅

*Make active filter nullable with three-state behavior*

### 1.1 RED: Write failing tests for active filter behavior ✅

**File**: [`tests/graphql/organizations/test_manufacturer_repository.py`](../../tests/graphql/organizations/test_manufacturer_repository.py)

**Test scenarios**:
- `test_search_active_true_filters_for_active_orgs` - When active=True, query filters for ACTIVE status
- `test_search_active_false_filters_for_inactive_orgs` - When active=False, query filters for non-ACTIVE status
- `test_search_active_none_does_not_filter_by_status` - When active=None, query does not filter by status

### 1.2 GREEN: Update repository to handle nullable active ✅

**File**: [`app/graphql/organizations/repositories/manufacturer_repository.py`](../../app/graphql/organizations/repositories/manufacturer_repository.py)

Changes:
- Change parameter type: `active: bool = True` → `active: bool | None = True`
- Update filter logic to use pattern matching (same pattern as `flow_connect_member`)

### 1.3 VERIFY: Run `task all` ✅

---

## Phase 2: Repository Layer - Connected Filter ✅

*Add connected subquery and filter at repository level*

### 2.1 RED: Write failing tests for connected filter ✅

**File**: [`tests/graphql/organizations/test_manufacturer_repository.py`](../../tests/graphql/organizations/test_manufacturer_repository.py)

**Test scenarios**:
- `test_search_returns_connected_status_in_result` - Query includes connected boolean
- `test_search_connected_true_filters_for_connected_orgs` - Filters for orgs with connections
- `test_search_connected_false_filters_for_unconnected_orgs` - Filters for orgs without connections
- `test_search_connected_none_does_not_filter` - Includes connected status but no filter

### 2.2 GREEN: Add connected subquery and filter to repository ✅

**File**: [`app/graphql/organizations/repositories/manufacturer_repository.py`](../../app/graphql/organizations/repositories/manufacturer_repository.py)

Changes:
- Add `user_org_id: uuid.UUID` parameter (required for connection subquery)
- Add `connected: bool | None = None` parameter
- Add `connection_exists` subquery (same pattern as `tenant_exists`)
- Add `connected` to select statement
- Add filter for `connected` parameter using pattern matching
- Update return type: `list[tuple[RemoteOrg, bool, bool]]` (org, flow_connect_member, connected)
- Lazy import for `RemoteConnection` and `ConnectionStatus` to avoid circular dependency

### 2.3 VERIFY: Repository tests pass ✅

*Note: Full `task all` deferred to Phase 3 - service needs update for new repository signature*

---

## Phase 3: Service Layer Updates ✅

*Update service to use new repository signature*

### 3.1 RED: Update service tests for new signature ✅

**File**: [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py)

Changes:
- Updated mocks to return 3-tuple `(org, is_member, is_connected)` instead of 2-tuple
- Added tests for `user_org_id` and `connected` filter being passed to repository
- Added test for nullable `active` filter

### 3.2 GREEN: Update service to use repository-level connected ✅

**File**: [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py)

Changes:
- Updated parameter: `active: bool = True` → `active: bool | None = True`
- Added parameter: `connected: bool | None = None`
- Pass `user_org_id` and `connected` to repository
- Removed second `get_user_org_and_connections()` call
- Updated result mapping to use `connected` from repository 3-tuple

### 3.3 VERIFY: Run `task all` ✅

---

## Phase 4: GraphQL Layer ✅

*Expose both filter changes in the GraphQL API*

### 4.1 GREEN: Update resolver parameters ✅

**File**: [`app/graphql/organizations/queries/manufacturer_queries.py`](../../app/graphql/organizations/queries/manufacturer_queries.py)

Changes:
- Updated parameter: `active: bool = True` → `active: bool | None = True`
- Added parameter: `connected: bool | None = None`
- Pass both to `service.search()`

### 4.2 VERIFY: Run `task all` and regenerate schema ✅

Schema updated:
```graphql
manufacturerSearch(
  searchTerm: String!
  active: Boolean = true
  flowConnectMember: Boolean = null
  connected: Boolean = null
  limit: Int! = 20
): [OrganizationLiteResponse!]!
```

---

## Phase 5: Verification ✅

*Manual testing via curl*

### 5.1 Manual verification ✅

| Test | Result |
|------|--------|
| Default (active=true) | ✅ Returns active orgs with connected status |
| `connected=true` | ✅ Only connected orgs |
| `connected=false` | ✅ Only unconnected orgs |
| `active=null` | ✅ All orgs regardless of status |
| `active=false` | ✅ Only inactive orgs (empty in test data) |
| Combined filters | ✅ Works correctly |

---

## Design Notes

**Why repository-level filtering?**

Both `active` and `connected` filters are implemented at the repository level using subqueries:

1. **Single query**: One DB round-trip instead of two
2. **Proper limit**: DB filters before applying limit, ensuring correct result count
3. **Consistent pattern**: Same approach as existing `flow_connect_member` filter
4. **Performance**: SQL engine optimized for subquery filtering (with proper indexes)

---

**⚠️ Index Recommendation (External DB)**

The `connection_exists` subquery requires indexes on `requester_org_id` and `target_org_id` in the `connections` table for optimal performance. Since `RemoteConnection` maps to an external database (`subscription.connections`), these indexes cannot be added via our migrations.

**Action for DBA team**: Verify/add indexes on `subscription.connections`:
```sql
CREATE INDEX idx_connections_requester_org_id ON subscription.connections(requester_org_id);
CREATE INDEX idx_connections_target_org_id ON subscription.connections(target_org_id);
```

Without these indexes, the subquery may cause performance degradation on large datasets.

---

**Lazy Import Workaround**

The `manufacturer_repository.py` uses a lazy import inside the `search()` method to avoid a circular dependency:

```python
# Lazy import to avoid circular dependency
from app.graphql.connections.models.enums import ConnectionStatus
from app.graphql.connections.models.remote_connection import RemoteConnection
```

**Root cause**: `app/graphql/organizations/__init__.py` eagerly imports `ManufacturerRepository`, which creates a cycle when importing `RemoteConnection` (which inherits from `OrgsBase`).

**Future improvement**: Consider refactoring the `__init__.py` exports to avoid eager loading of repositories.
