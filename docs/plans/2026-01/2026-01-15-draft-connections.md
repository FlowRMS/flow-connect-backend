# Draft Connections

- **Status**: ✅ Complete
- **Created**: 2026-01-15 16:41 -03
- **Approved**: 2026-01-15 16:55 -03
- **Finished**: 2026-01-15 19:24 -03
- **Commit Prefix**: Draft Connections

## Table of Contents

- [Overview](#overview)
- [Critical Files](#critical-files)
- [Phase 1: Add DRAFT Status to ConnectionStatus Enum](#phase-1-add-draft-status-to-connectionstatus-enum)
- [Phase 2: Update createConnection Mutation](#phase-2-update-createconnection-mutation)
- [Phase 3: Change OrganizationLiteResponse.connected to connectionStatus](#phase-3-change-organizationliteresponseconnected-to-connectionstatus)
- [Phase 4: Add inviteConnection Mutation](#phase-4-add-inviteconnection-mutation)
- [Phase 5: Verification](#phase-5-verification-)
- [Results](#results)

## Overview

Implement draft connections functionality:

1. **Add DRAFT status** - New connection status for draft connections
2. **Update createConnection** - Add `draft: bool = False` parameter
3. **Change connected field** - Rename `connected: bool` to `connectionStatus: ConnectionStatus | None`
4. **Add inviteConnection** - New mutation to change draft → pending via `/connections/org/:target_org_id/invite`

## Critical Files

| File | Purpose | Status |
|------|---------|--------|
| [`app/graphql/connections/models/enums.py`](../../app/graphql/connections/models/enums.py) | ConnectionStatus enum | ✅ |
| [`app/graphql/connections/mutations/connection_mutations.py`](../../app/graphql/connections/mutations/connection_mutations.py) | GraphQL mutations | ✅ |
| [`app/graphql/connections/services/connection_request_service.py`](../../app/graphql/connections/services/connection_request_service.py) | Remote API calls | ✅ |
| [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py) | OrganizationLiteResponse type | ✅ |
| [`app/graphql/organizations/repositories/manufacturer_repository.py`](../../app/graphql/organizations/repositories/manufacturer_repository.py) | Connection status query | ✅ |
| [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py) | ManufacturerSearchResult dataclass | ✅ |
| [`app/graphql/organizations/queries/manufacturer_queries.py`](../../app/graphql/organizations/queries/manufacturer_queries.py) | GraphQL query | ✅ |
| [`schema.graphql`](../../schema.graphql) | GraphQL schema | ✅ |
| [`tests/graphql/connections/test_connection_request_service.py`](../../tests/graphql/connections/test_connection_request_service.py) | Connection service tests | ✅ |
| [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py) | Manufacturer service tests | ✅ |

---

## Phase 1: Add DRAFT Status to ConnectionStatus Enum

Add the new DRAFT status to the existing enum.

### 1.1 GREEN: Add DRAFT to ConnectionStatus enum ✅

**File**: [`app/graphql/connections/models/enums.py`](../../app/graphql/connections/models/enums.py)

Add `DRAFT = "draft"` to the `ConnectionStatus` enum before PENDING.

### 1.2 VERIFY: Run `task all` ✅

Run type checks, linting, and tests to ensure no breaking changes.

---

## Phase 2: Update createConnection Mutation

Add the `draft` parameter to create draft or pending connections.

### 2.1 RED: Write failing tests for draft parameter ✅

**File**: [`tests/graphql/connections/test_connection_request_service.py`](../../tests/graphql/connections/test_connection_request_service.py)

**Test scenarios**:
- `test_create_without_draft_sends_draft_false` - Default behavior sends `draft: false`
- `test_create_with_draft_true_sends_draft_true` - Explicit draft=True is forwarded

### 2.2 GREEN: Add draft parameter to service and mutation ✅

**Files modified**:
1. [`app/graphql/connections/services/connection_request_service.py`](../../app/graphql/connections/services/connection_request_service.py)
   - Add `draft: bool = False` parameter to `create_connection_request()`
   - Include `"draft": draft` in the API payload

2. [`app/graphql/connections/mutations/connection_mutations.py`](../../app/graphql/connections/mutations/connection_mutations.py)
   - Add `draft: bool = False` parameter to `create_connection()` mutation
   - Pass `draft` to service method

3. [`schema.graphql`](../../schema.graphql)
   - Updated: `createConnection(targetOrgId: ID!, draft: Boolean! = false): Boolean!`

### 2.3 VERIFY: Run `task all` ✅

---

## Phase 3: Change OrganizationLiteResponse.connected to connectionStatus

Rename the `connected: bool` field to `connectionStatus: ConnectionStatus | None`.

**Note**: The `connected: Boolean` filter parameter in `manufacturerSearch` stays unchanged (filters by existence of any connection). Only the response field changes.

### 3.1 RED: Write failing tests for connectionStatus field ✅

**File**: [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py)

**Test scenarios**:
- `test_search_includes_connection_status_from_repository[draft-draft]` - Status DRAFT returned
- `test_search_includes_connection_status_from_repository[pending-pending]` - Status PENDING returned
- `test_search_includes_connection_status_from_repository[accepted-accepted]` - Status ACCEPTED returned
- `test_search_includes_connection_status_from_repository[None-None]` - No connection → None

### 3.2 GREEN: Implement connectionStatus changes ✅

**Files modified**:

1. [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py)
   - Register ConnectionStatus enum with strawberry
   - Change `connected: bool` → `connection_status: ConnectionStatus | None`
   - Update `from_orm_model()` factory method signature

2. [`app/graphql/organizations/repositories/manufacturer_repository.py`](../../app/graphql/organizations/repositories/manufacturer_repository.py)
   - Add scalar subquery to return the actual `status` instead of a boolean
   - Return `ConnectionStatus | None` instead of `bool`

3. [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py)
   - Update `ManufacturerSearchResult` dataclass: `connection_status: ConnectionStatus | None`
   - Update to pass `connection_status` instead of `connected`

4. [`app/graphql/organizations/queries/manufacturer_queries.py`](../../app/graphql/organizations/queries/manufacturer_queries.py)
   - Update the field mapping when calling `from_orm_model()`

5. [`schema.graphql`](../../schema.graphql)
   - Added `enum ConnectionStatus { DRAFT, PENDING, ACCEPTED, DECLINED }`
   - Updated `OrganizationLiteResponse`: `connectionStatus: ConnectionStatus`

### 3.3 REFACTOR: Clean up any redundant code ✅

No additional cleanup needed.

### 3.4 VERIFY: Run `task all` ✅

---

## Phase 4: Add inviteConnection Mutation

New mutation to change a connection from draft to pending.

### 4.1 RED: Write failing tests for invite service ✅

**File**: [`tests/graphql/connections/test_connection_request_service.py`](../../tests/graphql/connections/test_connection_request_service.py)

**Test scenarios**:
- `test_invite_calls_correct_endpoint` - POST to `/connections/org/{target_org_id}/invite`
- `test_invite_returns_true_on_success[200]` - Returns True on 200
- `test_invite_returns_true_on_success[201]` - Returns True on 201
- `test_invite_raises_not_found_on_404` - NotFoundError when connection not found
- `test_invite_raises_unauthorized_on_401_403[401]` - UnauthorizedError on 401
- `test_invite_raises_unauthorized_on_401_403[403]` - UnauthorizedError on 403

### 4.2 GREEN: Implement invite service and mutation ✅

**Files modified**:

1. [`app/graphql/connections/services/connection_request_service.py`](../../app/graphql/connections/services/connection_request_service.py)
   - Added `invite_connection(target_org_id: uuid.UUID) -> bool` method
   - POST to `/connections/org/{target_org_id}/invite`

2. [`app/graphql/connections/mutations/connection_mutations.py`](../../app/graphql/connections/mutations/connection_mutations.py)
   - Added `invite_connection(target_org_id: strawberry.ID) -> bool` mutation

3. [`schema.graphql`](../../schema.graphql)
   - Added: `inviteConnection(targetOrgId: ID!): Boolean!`

### 4.3 VERIFY: Run `task all` ✅

---

## Phase 5: Verification ✅

Manual verification in GraphQL Playground.

### 5.1 Test createConnection with draft parameter ✅

```graphql
mutation {
  createConnection(targetOrgId: "...", draft: true)
}
```

### 5.2 Test inviteConnection mutation ✅

```graphql
mutation {
  inviteConnection(targetOrgId: "...")
}
```

### 5.3 Test manufacturerSearch returns connectionStatus ✅

```graphql
query {
  manufacturerSearch(searchTerm: "test") {
    id
    name
    connectionStatus
  }
}
```

Verified:
- `connectionStatus` is `null` for unconnected orgs
- `connectionStatus` is `DRAFT`, `PENDING`, or `ACCEPTED` for connected orgs

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~2.5 hours |
| Phases | 5 |
| Files Modified | 10 |
| Tests Added | 10 |