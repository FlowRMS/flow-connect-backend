# Add Connected Field to ManufacturerSearch Query

- **Status**: ✅ Complete
- **Created**: 2026-01-14 19:36 -03
- **Finished**: 2026-01-14 22:04 -03
- **Code**: MSC (Manufacturer Search Connected)

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Database Models](#phase-1-database-models)
3. [Phase 2: Connections Package - Repository Layer](#phase-2-connections-package---repository-layer)
4. [Phase 3: GraphQL Layer Updates](#phase-3-graphql-layer-updates)
5. [Phase 4: Final Verification](#phase-4-final-verification)
6. [Critical Files](#critical-files)

---

## Overview

Add a `connected` field to the `manufacturerSearch` query that indicates whether each returned organization is connected with the logged-in user's organization.

### Requirements

1. **Connected Field**: Boolean indicating if orgs are connected
2. **Connection Logic**: Check `subscription.connections` table for connections where:
   - `requester_org_id` = user's org AND `target_org_id` = result org, OR
   - `target_org_id` = user's org AND `requester_org_id` = result org
   - Status is NOT "declined"
3. **User's Organization**: Obtained from `subscription.users.org_primary_id` using JWT subject (WorkOS user ID)
4. **Exclude Self**: User's own organization should not appear in results
5. **Error Handling** (fail-fast approach):
   - Throw `UserNotFoundError` when WorkOS user ID doesn't exist in remote DB
   - Throw `UserOrganizationRequiredError` when user exists but has no primary org

### Architecture Decision

Create a **new `connections` package** (`app/graphql/connections/`) to house all connection-related code. This package will initially work with the remote DB but is designed for future migration to the local DB.

**Package structure**:
```
app/graphql/connections/
├── __init__.py
├── exceptions.py
├── models/
│   ├── __init__.py
│   ├── remote_connection.py
│   └── enums.py
├── repositories/
│   ├── __init__.py
│   ├── connection_repository.py
│   └── user_org_repository.py
└── services/
    ├── __init__.py
    └── connection_service.py
```

---

## Phase 1: Database Models

_Create SQLAlchemy models in the new connections package._

### 1.1 GREEN: Create connections package structure ✅

Create package directories and `__init__.py` files.

### 1.2 GREEN: Create ConnectionStatus enum ✅

**File**: [`app/graphql/connections/models/enums.py`](../../app/graphql/connections/models/enums.py)

**Enum values**:
- `PENDING = "pending"`
- `ACCEPTED = "accepted"`
- `DECLINED = "declined"`

### 1.3 GREEN: Create RemoteConnection model ✅

**File**: [`app/graphql/connections/models/remote_connection.py`](../../app/graphql/connections/models/remote_connection.py)

**Data structure**:
- `id: Mapped[uuid.UUID]` - Primary key
- `requester_org_id: Mapped[uuid.UUID]` - Requesting organization
- `target_org_id: Mapped[uuid.UUID]` - Target organization
- `status: Mapped[str]` - Connection status (PostgreSQL enum type)
- `created_at: Mapped[datetime]`
- `updated_at: Mapped[datetime]`

**Table**: `subscription.connections`
**Base class**: `OrgsBase` (from organizations.models)

### 1.4 GREEN: Update RemoteUser model (in organizations package) ✅

**File**: [`app/graphql/organizations/models/remote_user.py`](../../app/graphql/organizations/models/remote_user.py)

**Add fields**:
- `workos_user_id: Mapped[str]` - WorkOS user identifier
- `org_primary_id: Mapped[uuid.UUID | None]` - User's primary organization

### 1.5 GREEN: Create custom exceptions ✅

**File**: [`app/graphql/connections/exceptions.py`](../../app/graphql/connections/exceptions.py)

**Exceptions**:
- `UserNotFoundError` - Raised when WorkOS user ID doesn't exist in remote DB
- `UserOrganizationRequiredError` - Raised when user exists but has no primary organization

### 1.6 GREEN: Export models from connections package ✅

**File**: [`app/graphql/connections/models/__init__.py`](../../app/graphql/connections/models/__init__.py)

### 1.7 VERIFY: Run `task all` ✅

---

## Phase 2: Connections Package - Repository Layer

_Create repositories for user org lookup and connection checking._

### 2.1 RED: Write failing tests for UserOrgRepository ✅

**File**: [`tests/graphql/connections/test_user_org_repository.py`](../../tests/graphql/connections/test_user_org_repository.py)

**Test scenarios**:
- `test_get_user_org_id_returns_org_id_for_valid_user` - Returns org_primary_id when user exists and has org
- `test_get_user_org_id_raises_error_for_unknown_user` - Raises UserNotFoundError when user not found
- `test_get_user_org_id_raises_error_for_user_without_org` - Raises UserOrganizationRequiredError when user has no primary org

### 2.2 GREEN: Implement UserOrgRepository ✅

**File**: [`app/graphql/connections/repositories/user_org_repository.py`](../../app/graphql/connections/repositories/user_org_repository.py)

**Class**: `UserOrgRepository`

**Constructor**: `session: AsyncSession`

**Method**: `get_user_org_id(workos_user_id: str) -> uuid.UUID`
- Raises `UserNotFoundError` if user not found
- Raises `UserOrganizationRequiredError` if user has no org_primary_id

### 2.3 RED: Write failing tests for ConnectionRepository ✅

**File**: [`tests/graphql/connections/test_connection_repository.py`](../../tests/graphql/connections/test_connection_repository.py)

**Test scenarios**:
- `test_get_connected_org_ids_returns_empty_set_when_no_connections` - No connections exist
- `test_get_connected_org_ids_returns_ids_where_user_is_requester` - User org is requester
- `test_get_connected_org_ids_returns_ids_where_user_is_target` - User org is target
- `test_get_connected_org_ids_excludes_declined_connections` - Declined status excluded

### 2.4 GREEN: Implement ConnectionRepository ✅

**File**: [`app/graphql/connections/repositories/connection_repository.py`](../../app/graphql/connections/repositories/connection_repository.py)

**Class**: `ConnectionRepository`

**Constructor**: `session: AsyncSession`

**Method**: `get_connected_org_ids(user_org_id: uuid.UUID, candidate_org_ids: list[uuid.UUID]) -> set[uuid.UUID]`
- Query both directions (user as requester OR target)
- Filter: `status != 'declined'` (cast to String for PostgreSQL enum comparison)

### 2.5 GREEN: Create ConnectionService (facade for manufacturer search) ✅

**File**: [`app/graphql/connections/services/connection_service.py`](../../app/graphql/connections/services/connection_service.py)

**Class**: `ConnectionService`

**Constructor**:
- `user_org_repository: UserOrgRepository`
- `connection_repository: ConnectionRepository`

**Method**: `get_user_org_and_connections(workos_user_id: str, candidate_org_ids: list[uuid.UUID]) -> tuple[uuid.UUID, set[uuid.UUID]]`
- Returns user's org_id and set of connected org IDs
- Propagates `UserNotFoundError` and `UserOrganizationRequiredError` from repository

### 2.6 GREEN: Export repositories from connections package ✅

**File**: [`app/graphql/connections/repositories/__init__.py`](../../app/graphql/connections/repositories/__init__.py)

### 2.7 VERIFY: Run `task all` ✅

---

## Phase 3: GraphQL Layer Updates

_Update manufacturer search to include connected field._

### 3.1 RED: Update tests for connected field in ManufacturerService ✅

**File**: [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py)

**New test scenarios**:
- `test_search_includes_connected_field_true_for_connected_orgs` - Orgs with active connection show connected=True
- `test_search_includes_connected_field_false_for_unconnected_orgs` - Orgs without connection show connected=False
- `test_search_excludes_user_own_organization` - User's own org never appears in results
- `test_search_raises_error_when_user_not_found` - Propagates UserNotFoundError from connection service
- `test_search_raises_error_when_user_has_no_org` - Propagates UserOrganizationRequiredError from connection service

### 3.2 GREEN: Update ManufacturerSearchResult dataclass ✅

**File**: [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py)

**Add field**: `connected: bool`

### 3.3 GREEN: Update ManufacturerService ✅

**File**: [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py)

**Constructor changes**: Add dependencies
- `connection_service: ConnectionService`
- `auth_info: AuthInfo`

**Method `search()` changes**:
1. Get user org + connected IDs via `connection_service.get_user_org_and_connections()`
2. Pass `exclude_org_id` to repository
3. Set `connected=True` for orgs in connected set

### 3.4 GREEN: Update ManufacturerRepository ✅

**File**: [`app/graphql/organizations/repositories/manufacturer_repository.py`](../../app/graphql/organizations/repositories/manufacturer_repository.py)

**Method `search()` changes**:
- Add parameter: `exclude_org_id: uuid.UUID | None = None`
- Add filter when provided

### 3.5 GREEN: Update OrganizationLiteResponse ✅

**File**: [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py)

**Add field**: `connected: bool`
**Update `from_orm_model()`**: Add `connected: bool = False` parameter

### 3.6 GREEN: Update ManufacturerQueries resolver ✅

**File**: [`app/graphql/organizations/queries/manufacturer_queries.py`](../../app/graphql/organizations/queries/manufacturer_queries.py)

Pass `connected` to response factory.

### 3.7 VERIFY: Run `task all` ✅

---

## Phase 4: Final Verification

### 4.1 Generate GraphQL schema ✅

Run: `task gql`

Confirm `connected: Boolean!` added to `OrganizationLiteResponse`.

### 4.2 Manual testing in GraphQL Playground ✅

**Corrections during verification:**
- Removed `deleted_at` field from `RemoteConnection` model (column doesn't exist in DB)
- Added `cast(status, String)` for PostgreSQL enum comparison in `ConnectionRepository`

**Test query**:
```graphql
query {
  manufacturerSearch(searchTerm: "acme") {
    id
    name
    flowConnectMember
    connected
  }
}
```

---

## Critical Files

| File | Purpose | Status |
|------|---------|--------|
| [`app/graphql/connections/exceptions.py`](../../app/graphql/connections/exceptions.py) | UserNotFoundError, UserOrganizationRequiredError | ✅ |
| [`app/graphql/connections/models/enums.py`](../../app/graphql/connections/models/enums.py) | ConnectionStatus enum | ✅ |
| [`app/graphql/connections/models/remote_connection.py`](../../app/graphql/connections/models/remote_connection.py) | RemoteConnection model | ✅ |
| [`app/graphql/connections/repositories/user_org_repository.py`](../../app/graphql/connections/repositories/user_org_repository.py) | Get user's org ID (with error handling) | ✅ |
| [`app/graphql/connections/repositories/connection_repository.py`](../../app/graphql/connections/repositories/connection_repository.py) | Check connections | ✅ |
| [`app/graphql/connections/services/connection_service.py`](../../app/graphql/connections/services/connection_service.py) | Facade service | ✅ |
| [`app/graphql/organizations/models/remote_user.py`](../../app/graphql/organizations/models/remote_user.py) | Add workos_user_id, org_primary_id | ✅ |
| [`app/graphql/organizations/repositories/manufacturer_repository.py`](../../app/graphql/organizations/repositories/manufacturer_repository.py) | Exclude user's org | ✅ |
| [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py) | Orchestrate connected logic | ✅ |
| [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py) | Add connected field | ✅ |
| [`tests/graphql/connections/test_user_org_repository.py`](../../tests/graphql/connections/test_user_org_repository.py) | Tests for user org lookup | ✅ |
| [`tests/graphql/connections/test_connection_repository.py`](../../tests/graphql/connections/test_connection_repository.py) | Tests for connection check | ✅ |
| [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py) | Tests for connected field | ✅ |
