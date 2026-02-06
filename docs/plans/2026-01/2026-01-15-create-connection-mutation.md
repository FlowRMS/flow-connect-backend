# Create Connection Mutation

- **Status**: ✅ Complete
- **Created**: 2026-01-15 08:35 -03
- **Finished**: 2026-01-15 11:38 -03
- **Code**: CCM

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Configuration](#phase-1-configuration)
3. [Phase 2: HTTP Client](#phase-2-http-client)
4. [Phase 3: Connection Request Service](#phase-3-connection-request-service)
5. [Phase 4: GraphQL Mutation](#phase-4-graphql-mutation)
6. [Phase 5: Final Verification](#phase-5-final-verification-)
7. [Critical Files](#critical-files)
8. [Notes](#notes)

---

## Overview

Add a `createConnection` mutation that sends a connection request to a remote REST API.

### Requirements

| Requirement | Details |
|-------------|---------|
| Mutation | `createConnection(targetOrgId: ID!) -> Boolean!` |
| Remote API | POST `/connections/requests` with body `{"target_org_id": "uuid"}` |
| Authentication | Forward bearer token from `AuthInfo.access_token` |
| Base URL | Environment variable `FLOW_CONNECT_API_URL` |
| Return | `true` on 2xx response |

### Error Mapping

| HTTP Status | Exception |
|-------------|-----------|
| 400 | `RemoteApiError` (with remote message extracted) |
| 401, 403 | `UnauthorizedError` |
| 404 | `NotFoundError` |
| 409 | `ConflictError` |
| 5xx, network | `RemoteApiError` |

### Architecture

```
GraphQL Mutation
    │
    ▼
ConnectionRequestService
    │
    ▼
FlowConnectApiClient (httpx)
    │
    ▼
Remote REST API (POST /connections/requests)
```

---

## Phase 1: Configuration

_Add environment configuration for the remote API._

### 1.1 GREEN: Create FlowConnectApiSettings ✅

**File**: [`app/core/config/flow_connect_api_settings.py`](../../app/core/config/flow_connect_api_settings.py)

**Data structure**:
- `flow_connect_api_url: str` - Base URL (e.g., `https://api.flowrms.com`)

Follow `WorkOSSettings` pattern with `SettingsConfigDict`.

### 1.2 GREEN: Register settings in providers ✅

**File**: [`app/core/providers.py`](../../app/core/providers.py)

Add `FlowConnectApiSettings` to `settings_classes` list.

### 1.3 VERIFY: Run `task all` ✅

---

## Phase 2: HTTP Client

_Create an HTTP client for authenticated API calls._

### 2.1 RED: Write failing tests for FlowConnectApiClient ✅

**File**: [`tests/core/flow_connect_api/test_flow_connect_api_client.py`](../../tests/core/flow_connect_api/test_flow_connect_api_client.py)

**Test scenarios**:
- `test_post_includes_authorization_header` - Request includes Bearer token
- `test_post_sends_json_body` - Request body is JSON with correct content
- `test_post_returns_response` - Returns httpx.Response object
- `test_post_raises_remote_api_error_on_network_failure` - Network errors wrapped in RemoteApiError

### 2.2 GREEN: Create RemoteApiError exception ✅

**File**: [`app/errors/common_errors.py`](../../app/errors/common_errors.py)

Add `RemoteApiError(StrawberryGraphQLError)` with optional `status_code`.

### 2.3 GREEN: Implement FlowConnectApiClient ✅

**File**: [`app/core/flow_connect_api/flow_connect_api_client.py`](../../app/core/flow_connect_api/flow_connect_api_client.py)

**Class**: `FlowConnectApiClient`

**Constructor**:
- `settings: FlowConnectApiSettings`
- `auth_info: AuthInfo`

**Method**: `async def post(self, endpoint: str, body: dict[str, Any]) -> httpx.Response`
- Uses `httpx.AsyncClient` as context manager
- Adds `Authorization: Bearer {token}` header
- Wraps `httpx.RequestError` in `RemoteApiError`

### 2.4 GREEN: Register client with DI ✅

**File**: [`app/graphql/di/api_client_providers.py`](../../app/graphql/di/api_client_providers.py)

Manual provider registration for `FlowConnectApiClient`.

**File**: `app/core/providers.py`

Add `api_client_providers` to `modules` list.

### 2.5 VERIFY: Run `task all` ✅

---

## Phase 3: Connection Request Service

_Create service that uses the API client to create connections._

### 3.1 RED: Write failing tests for ConnectionRequestService ✅

**File**: [`tests/graphql/connections/test_connection_request_service.py`](../../tests/graphql/connections/test_connection_request_service.py)

**Test scenarios**:
- `test_create_returns_true_on_2xx` - 200/201 response returns True
- `test_raises_unauthorized_on_401_403` - Auth errors
- `test_raises_not_found_on_404` - Target org not found
- `test_raises_conflict_on_409` - Connection already exists
- `test_raises_remote_api_error_on_5xx` - Server errors
- `test_propagates_remote_api_error` - Network errors pass through

### 3.2 GREEN: Implement ConnectionRequestService ✅

**File**: [`app/graphql/connections/services/connection_request_service.py`](../../app/graphql/connections/services/connection_request_service.py)

**Class**: `ConnectionRequestService`

**Constructor**: `api_client: FlowConnectApiClient`

**Method**: `async def create_connection_request(self, target_org_id: uuid.UUID) -> bool`
- Calls `api_client.post("/connections/requests", {"target_org_id": str(target_org_id)})`
- Maps status codes to exceptions (see error mapping table)
- Returns `True` for 2xx

### 3.3 VERIFY: Run `task all` ✅

---

## Phase 4: GraphQL Mutation

_Add the createConnection mutation._

### 4.1 GREEN: Create ConnectionMutations class ✅

**File**: [`app/graphql/connections/mutations/connection_mutations.py`](../../app/graphql/connections/mutations/connection_mutations.py)

**Class**: `ConnectionMutations`

**Mutation**:
```python
@strawberry.mutation()
@inject
async def create_connection(
    self,
    target_org_id: strawberry.ID,
    service: Injected[ConnectionRequestService],
) -> bool:
```

### 4.2 GREEN: Update schema to include mutations ✅

**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

Make `Mutation` inherit from `ConnectionMutations`.

### 4.3 GREEN: Generate GraphQL schema ✅

Run: `task gql`

### 4.4 VERIFY: Run `task all` ✅

---

## Phase 5: Final Verification ✅

_Manual testing in GraphQL Playground._

### 5.1 Test mutation ✅

```graphql
mutation {
  createConnection(targetOrgId: "9133da7c-3b98-4673-91dc-0dc58cc8740c")
}
```

**Test cases**:
1. Valid target org -> Returns `true`
2. Non-existent target -> `NotFoundError`
3. Already connected -> `ConflictError`
4. Invalid token -> `UnauthorizedError`

---

## Critical Files

| File | Purpose | Status |
|------|---------|--------|
| [`app/core/config/flow_connect_api_settings.py`](../../app/core/config/flow_connect_api_settings.py) | API base URL config | ✅ |
| [`app/errors/common_errors.py`](../../app/errors/common_errors.py) | Add RemoteApiError | ✅ |
| [`app/core/flow_connect_api/__init__.py`](../../app/core/flow_connect_api/__init__.py) | Package exports | ✅ |
| [`app/core/flow_connect_api/flow_connect_api_client.py`](../../app/core/flow_connect_api/flow_connect_api_client.py) | HTTP client | ✅ |
| [`app/core/flow_connect_api/response_handler.py`](../../app/core/flow_connect_api/response_handler.py) | HTTP status to exception mapping | ✅ |
| [`app/graphql/di/api_client_providers.py`](../../app/graphql/di/api_client_providers.py) | DI registration | ✅ |
| [`app/graphql/connections/services/connection_request_service.py`](../../app/graphql/connections/services/connection_request_service.py) | Service layer | ✅ |
| [`app/graphql/connections/mutations/connection_mutations.py`](../../app/graphql/connections/mutations/connection_mutations.py) | GraphQL mutation | ✅ |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | Register mutation | ✅ |
| [`tests/core/flow_connect_api/test_flow_connect_api_client.py`](../../tests/core/flow_connect_api/test_flow_connect_api_client.py) | Client tests | ✅ |
| [`tests/graphql/connections/test_connection_request_service.py`](../../tests/graphql/connections/test_connection_request_service.py) | Service tests | ✅ |

---

## Notes

### Ad-hoc fix: JWT token handling

During Phase 5 manual testing, we discovered that `app/auth/workos_service.py` required the `external_id` claim in JWT tokens. This caused authentication failures for tokens without this claim.

**Fix applied** to [`app/auth/workos_service.py`](../../app/auth/workos_service.py):
- Made `external_id` optional in JWT token validation
- When `external_id` is present → use it directly as `flow_user_id` (it's a UUID)
- When `external_id` is absent → generate a deterministic UUID from `sub` using `uuid.uuid5(uuid.NAMESPACE_URL, sub)`

This ensures consistent user identification across sessions while supporting both token formats.
