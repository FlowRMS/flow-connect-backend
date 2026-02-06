# WorkOS Organization Webhook - Tenant Auto-Provisioning

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1329](https://linear.app/flow-labs/issue/FLO-1329/flowpos-create-db-and-install-schemas)
- **Created**: 2026-01-27 11:45 -03
- **Approved**: 2026-01-27 12:31 -03
- **Finished**: 2026-01-28 11:43 -03
- **PR**: [#23](https://github.com/FlowRMS/flow-py-connect/pull/23)
- **Commit Prefix**: WorkOS Org Webhook

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [WorkOS Dashboard Setup](#workos-dashboard-setup)
- [Critical Files](#critical-files)
- [Phase 1: Webhook Endpoint Foundation](#phase-1-webhook-endpoint-foundation)
- [Phase 2: Tenant Provisioning Service](#phase-2-tenant-provisioning-service)
- [Phase 3: Database Creation Service](#phase-3-database-creation-service)
- [Phase 4: Migration Execution Service](#phase-4-migration-execution-service)
- [Phase 5: Integration & End-to-End Flow](#phase-5-integration--end-to-end-flow)
- [Phase 6: Router Registration](#phase-6-router-registration)
- [Phase 7: Verification](#phase-7-verification)
- [Results](#results)

---

## Overview

Implement automatic tenant provisioning when a new organization is created in WorkOS. This involves:

1. **Webhook Endpoint**: Receive `organization.created` events from WorkOS
2. **Signature Verification**: Validate webhook authenticity using HMAC SHA256
3. **Tenant Check**: Verify if organization already exists in `public.tenants`
4. **Database Creation**: Create a new PostgreSQL database for the tenant if needed
5. **Migration Execution**: Apply Alembic migrations to the new database

### Design Patterns Used

- **Webhook Pattern** ([Enterprise Integration Patterns, Hohpe & Woolf](https://www.enterpriseintegrationpatterns.com/)): Asynchronous event-driven integration
- **Factory Pattern** ([GoF](https://en.wikipedia.org/wiki/Factory_method_pattern)): Database/tenant creation abstraction
- **Strategy Pattern** ([GoF](https://en.wikipedia.org/wiki/Strategy_pattern)): Pluggable signature verification

---

## Architecture

### Webhook Flow

```
WorkOS Dashboard                   Flow Connect
      │                                 │
      │  POST /webhooks/workos          │
      │  (organization.created)         │
      ├────────────────────────────────>│
      │                                 │
      │                    1. Verify Signature
      │                    2. Parse Event
      │                    3. Check Tenant Exists
      │                    4. Create Tenant Row
      │                    5. Create Database
      │                    6. Run Migrations
      │                                 │
      │         HTTP 200 OK             │
      │<────────────────────────────────┤
```

### Database Tables Involved

| | **`public.tenants`** | |
|-----|------|-------|
| **Column** | **Type** | **Constraints** |
| `id` | `UUID` | PK |
| `org_id` | `String` | NOT NULL |
| `initialize` | `Boolean` | NOT NULL |
| `name` | `String(255)` | NOT NULL |
| `url` | `String(255)` | NOT NULL, UNIQUE |
| `database` | `String(255)` | NOT NULL |
| `read_only_database` | `String(255)` | NOT NULL |
| `username` | `String(255)` | NOT NULL |
| `alembic_version` | `String(50)` | NOT NULL |

### WorkOS Event Payload Structure

```json
{
  "id": "event_01ABC...",
  "event": "organization.created",
  "created_at": "2026-01-27T14:00:00Z",
  "data": {
    "id": "org_01XYZ...",
    "name": "Acme Corp",
    "object": "organization",
    "external_id": "external-123",
    "domains": [...],
    "created_at": "2026-01-27T14:00:00Z",
    "updated_at": "2026-01-27T14:00:00Z"
  }
}
```

---

## WorkOS Dashboard Setup

Configure the webhook in WorkOS Dashboard after deployment.

### Step 1: Set Environment Variable

Add `WORKOS_WEBHOOK_SECRET` to the environment **before** deploying:

| Environment | File |
|-------------|------|
| Local | `.env.local` |
| Staging | `.env.staging` |
| Production | `.env.production` |

```
WORKOS_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx
```

**Note**: The secret will be generated in Step 3. You can use a placeholder initially.

### Step 2: Deploy the Application

Deploy the application so the webhook endpoint is accessible:

| Environment | Webhook URL |
|-------------|-------------|
| Staging | `https://api.staging.flowrms.com/webhooks/workos` |
| Production | `https://api.flowrms.com/webhooks/workos` |

### Step 3: Configure WorkOS Dashboard

1. Navigate to [WorkOS Dashboard](https://dashboard.workos.com/) → **Webhooks**
2. Click **Add Endpoint**
3. Enter the webhook URL for your environment (see Step 2)
4. Select the `organization.created` event type
5. Click **Create**
6. Copy the **Webhook Secret** and update the environment variable from Step 1
7. Redeploy if the secret was a placeholder

### Step 4: Verify

1. Create a new organization in WorkOS
2. Check application logs for: `Received WorkOS webhook`
3. Verify tenant was created in `public.tenants`
4. Verify database was created and migrations applied

---

## Critical Files

| File | Description | Status |
|------|-------------|--------|
| [`app/webhooks/__init__.py`](../../app/webhooks/__init__.py) | Webhooks module init | ✅ |
| [`app/webhooks/workos/__init__.py`](../../app/webhooks/workos/__init__.py) | WorkOS webhooks module init | ✅ |
| [`app/webhooks/workos/router.py`](../../app/webhooks/workos/router.py) | FastAPI router for WorkOS webhooks | ✅ |
| [`app/webhooks/workos/signature.py`](../../app/webhooks/workos/signature.py) | Webhook signature verification | ✅ |
| [`app/webhooks/workos/schemas.py`](../../app/webhooks/workos/schemas.py) | Pydantic schemas for webhook payloads | ✅ |
| [`app/webhooks/workos/handlers.py`](../../app/webhooks/workos/handlers.py) | Event handlers (organization.created) | ✅ |
| [`app/core/config/workos_settings.py`](../../app/core/config/workos_settings.py) | Add webhook secret to settings | ✅ |
| [`app/tenant_provisioning/__init__.py`](../../app/tenant_provisioning/__init__.py) | Tenant provisioning module init | ✅ |
| [`app/tenant_provisioning/service.py`](../../app/tenant_provisioning/service.py) | TenantProvisioningService | ✅ |
| [`app/tenant_provisioning/repository.py`](../../app/tenant_provisioning/repository.py) | TenantRepository (public.tenants access) | ✅ |
| [`app/tenant_provisioning/database_service.py`](../../app/tenant_provisioning/database_service.py) | Database creation service | ✅ |
| [`app/tenant_provisioning/migration_service.py`](../../app/tenant_provisioning/migration_service.py) | Migration execution service | ✅ |
| [`app/api/app.py`](../../app/api/app.py) | Register webhook router | ✅ |
| [`tests/webhooks/workos/test_signature.py`](../../tests/webhooks/workos/test_signature.py) | Signature verification tests | ✅ |
| [`tests/webhooks/workos/test_handlers.py`](../../tests/webhooks/workos/test_handlers.py) | Handler tests | ✅ |
| [`tests/tenant_provisioning/test_service.py`](../../tests/tenant_provisioning/test_service.py) | Provisioning service tests | ✅ |
| [`tests/tenant_provisioning/test_repository.py`](../../tests/tenant_provisioning/test_repository.py) | Repository tests | ✅ |
| [`tests/webhooks/workos/test_router.py`](../../tests/webhooks/workos/test_router.py) | Router tests | ✅ |
| [`tests/webhooks/workos/test_webhook_integration.py`](../../tests/webhooks/workos/test_webhook_integration.py) | Integration tests | ✅ |

---

## Phase 1: Webhook Endpoint Foundation

Set up the FastAPI webhook endpoint with signature verification.

### 1.1 RED: Write failing tests for signature verification ✅

**File**: [`tests/webhooks/workos/test_signature.py`](../../tests/webhooks/workos/test_signature.py)

**Test scenarios**:
- `test_verify_valid_signature` - Valid HMAC signature returns True
- `test_verify_invalid_signature` - Invalid signature returns False
- `test_verify_expired_timestamp` - Timestamp older than tolerance (5 min) returns False
- `test_verify_missing_header` - Missing WorkOS-Signature header raises error
- `test_parse_signature_header` - Correctly extracts timestamp and hash from header

### 1.2 GREEN: Implement signature verification ✅

**Files**:
- [`app/webhooks/workos/signature.py`](../../app/webhooks/workos/signature.py)
  - `parse_signature_header(header: str) -> tuple[int, str]` - Extract `t=timestamp` and `v1=hash`
  - `verify_signature(payload: bytes, header: str, secret: str, tolerance: int = 300) -> bool`
  - Uses HMAC SHA256: `HMAC(secret, f"{timestamp}.{payload}")`

- [`app/core/config/workos_settings.py`](../../app/core/config/workos_settings.py)
  - Add `workos_webhook_secret: str` field

### 1.3 RED: Write failing tests for webhook endpoint ✅

**File**: [`tests/webhooks/workos/test_router.py`](../../tests/webhooks/workos/test_router.py)

**Test scenarios**:
- `test_webhook_valid_signature_returns_200` - Valid request returns 200
- `test_webhook_invalid_signature_returns_401` - Invalid signature returns 401
- `test_webhook_unknown_event_returns_200` - Unknown event types are acknowledged (logged, not processed)
- `test_webhook_organization_created_triggers_handler` - organization.created calls handler

### 1.4 GREEN: Implement webhook router ✅

**Files**:
- [`app/webhooks/__init__.py`](../../app/webhooks/__init__.py) - Module init
- [`app/webhooks/workos/__init__.py`](../../app/webhooks/workos/__init__.py) - Module init
- [`app/webhooks/workos/schemas.py`](../../app/webhooks/workos/schemas.py)
  - `WorkOSOrganizationData` - Organization fields (id, name, external_id, domains, etc.)
  - `WorkOSEvent` - Event wrapper (id, event, created_at, data)
- [`app/webhooks/workos/router.py`](../../app/webhooks/workos/router.py)
  - `POST /webhooks/workos` endpoint
  - Signature verification middleware
  - Event routing to handlers

### 1.5 REFACTOR: Clean up, ensure type safety ✅

### 1.6 VERIFY: Run `task all` ✅

---

## Phase 2: Tenant Provisioning Service

Create the service layer for tenant provisioning.

### 2.1 RED: Write failing tests for TenantRepository ✅

**File**: [`tests/tenant_provisioning/test_repository.py`](../../tests/tenant_provisioning/test_repository.py)

**Test scenarios**:
- `test_get_by_org_id_found` - Returns tenant when org_id exists
- `test_get_by_org_id_not_found` - Returns None when org_id doesn't exist
- `test_create_tenant` - Creates new tenant row with correct fields
- `test_update_initialize_flag` - Sets initialize=True after provisioning

### 2.2 GREEN: Implement TenantRepository ✅

**File**: [`app/tenant_provisioning/repository.py`](../../app/tenant_provisioning/repository.py)

- `TenantRepository`
  - `get_by_org_id(org_id: str) -> Tenant | None`
  - `create(tenant: Tenant) -> Tenant`
  - `update_initialize(tenant_id: UUID, initialize: bool) -> None`
  - Uses `public.tenants` table via commons `Tenant` model

### 2.3 RED: Write failing tests for TenantProvisioningService ✅

**File**: [`tests/tenant_provisioning/test_service.py`](../../tests/tenant_provisioning/test_service.py)

**Test scenarios**:
- `test_provision_new_tenant_creates_all_resources` - Full flow for new org
- `test_provision_existing_tenant_skips_creation` - No-op if tenant exists
- `test_provision_generates_correct_database_name` - Database name derived from org name
- `test_provision_handles_database_creation_failure` - Proper error handling

### 2.4 GREEN: Implement TenantProvisioningService ✅

**File**: [`app/tenant_provisioning/service.py`](../../app/tenant_provisioning/service.py)

- `TenantProvisioningService`
  - `provision(org_id: str, org_name: str) -> ProvisioningResult`
  - Orchestrates: check → create tenant → create db → run migrations → set initialize=True
  - `generate_database_url(org_name: str) -> str` - Sanitize org name to valid DB name

### 2.5 REFACTOR: Clean up, ensure type safety ✅

### 2.6 VERIFY: Run `task all` ✅

---

## Phase 3: Database Creation Service

Create the service for PostgreSQL database creation.

### 3.1 RED: Write failing tests for DatabaseCreationService ✅

**File**: [`tests/tenant_provisioning/test_database_service.py`](../../tests/tenant_provisioning/test_database_service.py)

**Test scenarios**:
- `test_database_exists_returns_true` - Detects existing database
- `test_database_not_exists_returns_false` - Detects missing database
- `test_create_database_success` - Creates new PostgreSQL database
- `test_create_database_sanitizes_name` - Database name properly quoted

### 3.2 GREEN: Implement DatabaseCreationService ✅

**File**: [`app/tenant_provisioning/database_service.py`](../../app/tenant_provisioning/database_service.py)

- `DatabaseCreationService`
  - `database_exists(db_name: str) -> bool` - Query `pg_database`
  - `create_database(db_name: str) -> None` - `CREATE DATABASE` command
  - Uses raw asyncpg (CREATE DATABASE cannot run in transaction)

### 3.3 REFACTOR: Clean up, ensure type safety ✅

### 3.4 VERIFY: Run `task all` ✅

---

## Phase 4: Migration Execution Service

Create the service for running Alembic migrations on tenant databases.

### 4.1 RED: Write failing tests for MigrationService ✅

**File**: [`tests/tenant_provisioning/test_migration_service.py`](../../tests/tenant_provisioning/test_migration_service.py)

**Test scenarios**:
- `test_get_current_revision_empty_db` - Returns None for uninitialized DB
- `test_get_current_revision_migrated_db` - Returns version string
- `test_run_migrations_applies_all` - Migrations applied successfully
- `test_run_migrations_creates_schema` - Schema created if needed

### 4.2 GREEN: Implement MigrationService ✅

**File**: [`app/tenant_provisioning/migration_service.py`](../../app/tenant_provisioning/migration_service.py)

- `MigrationService`
  - `get_current_revision(db_url: str) -> str | None`
  - `run_migrations(db_url: str) -> str` - Returns new revision
  - Uses Alembic programmatic API with `run_in_executor` for async compatibility

### 4.3 REFACTOR: Clean up, ensure type safety ✅

### 4.4 VERIFY: Run `task all` ✅

---

## Phase 5: Integration & End-to-End Flow

Wire everything together and create the event handler.

### 5.1 RED: Write failing tests for organization.created handler ✅

**File**: [`tests/webhooks/workos/test_handlers.py`](../../tests/webhooks/workos/test_handlers.py)

**Test scenarios**:
- `test_handle_organization_created_new_org` - Full provisioning flow
- `test_handle_organization_created_existing_org` - Logs and skips
- `test_handle_organization_created_failure_logged` - Errors are logged, not raised

### 5.2 GREEN: Implement handler and wire dependencies ✅

**Files**:
- [`app/webhooks/workos/handlers.py`](../../app/webhooks/workos/handlers.py)
  - `handle_organization_created(event: WorkOSEvent, provisioning_service: TenantProvisioningService) -> None`
  - Calls `TenantProvisioningService.provision()`

- [`app/webhooks/workos/router.py`](../../app/webhooks/workos/router.py)
  - Updated `create_workos_webhook_router()` to accept `provisioning_service` parameter
  - Passes provisioning_service to handler

- [`tests/webhooks/workos/test_webhook_integration.py`](../../tests/webhooks/workos/test_webhook_integration.py)
  - Integration test simulating full WorkOS webhook flow (3 tests)

### 5.3 REFACTOR: Clean up, ensure type safety ✅

### 5.4 VERIFY: Run `task all` ✅

24 webhook tests passing, 318 total tests passing.

---

## Phase 6: Router Registration ✅

Register the WorkOS webhook router in the FastAPI application.

### 6.1 GREEN: Register webhook router ✅

**File**: [`app/api/app.py`](../../app/api/app.py)

Router registration was completed during Phase 5 integration:
- Import `create_workos_webhook_router` from `app.webhooks.workos.router`
- Create `SessionScopedProvisioningService` for session management
- Register conditionally when `WORKOS_WEBHOOK_SECRET` is configured

### 6.2 VERIFY: Run `task all` ✅

---

## Phase 7: Verification ✅

Manual testing of the webhook endpoint and tenant provisioning flow.

### 7.1 Configure environment ✅

`WORKOS_WEBHOOK_SECRET` already configured in `.env.local`.

### 7.2 Test webhook endpoint ✅

**Test scenarios**:
- ✅ Execute webhook with valid signature - Tenant created (ID `385e006c-c298-4b88-a3dd-16c169260ab8`)
- ✅ Verify database created - Database created on Neon
- ✅ Verify migrations applied - 8 migrations executed successfully

---

## Results

| Metric | Value |
|--------|-------|
| Phases Completed | 7 |
| Files Created | 23 |
| Files Modified | 3 |
| Tests Added | 46 |

### Files Created

**App modules:**
- `app/webhooks/__init__.py`
- `app/webhooks/workos/__init__.py`
- `app/webhooks/workos/signature.py`
- `app/webhooks/workos/schemas.py`
- `app/webhooks/workos/handlers.py`
- `app/webhooks/workos/router.py`
- `app/tenant_provisioning/__init__.py`
- `app/tenant_provisioning/repository.py`
- `app/tenant_provisioning/service.py`
- `app/tenant_provisioning/database_service.py`
- `app/tenant_provisioning/migration_service.py`

**Test modules:**
- `tests/webhooks/__init__.py`
- `tests/webhooks/workos/__init__.py`
- `tests/webhooks/workos/conftest.py`
- `tests/webhooks/workos/test_signature.py`
- `tests/webhooks/workos/test_router.py`
- `tests/webhooks/workos/test_handlers.py`
- `tests/webhooks/workos/test_webhook_integration.py`
- `tests/tenant_provisioning/__init__.py`
- `tests/tenant_provisioning/test_repository.py`
- `tests/tenant_provisioning/test_service.py`
- `tests/tenant_provisioning/test_database_service.py`
- `tests/tenant_provisioning/test_migration_service.py`

