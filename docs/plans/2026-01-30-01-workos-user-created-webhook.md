# WorkOS User Created Webhook

- **Status**: Complete
- **Linear Task**: [FLO-1363](https://linear.app/flow-labs/issue/FLO-1363/add-a-webhook-when-a-user-gets-created-in-workos-to-ensure-that-user)
- **Created**: 2026-01-30 13:29 -03
- **Approved**: 2026-01-30 14:18 -03
- **Finished**: 2026-02-02 15:52 -03
- **PR**: [#172](https://github.com/FlowRMS/flow-py-backend/pull/172)
- **Commit Prefix**: WorkOS User Webhook

---

## Table of Contents

- [Overview](#overview)
- [Critical Files](#critical-files)
- [Phase 1: Webhook Infrastructure](#phase-1-webhook-infrastructure)
- [Phase 2: User Sync Service](#phase-2-user-sync-service)
- [Phase 3: Application Integration](#phase-3-application-integration)
- [Phase 4: Verification](#phase-4-verification)
- [Changes During Review](#changes-during-review)
- [Results](#results)

---

## Overview

Create a listener for WorkOS webhooks when a user is created in WorkOS. The webhook handler will ensure user synchronization between WorkOS and the local database.

### Business Logic

When a `user.created` event is received from WorkOS:

1. **Skip if external_id exists** - If the WorkOS user already has an `external_id`, do nothing (user was created from our system)
2. **Skip if no organization** - If the WorkOS user has no organization membership, do nothing
3. **Resolve tenant** - Look up `Tenant` by WorkOS `org_id` to get the tenant database
4. **Check existing user by email** - Look up the user in `PyUser.Users` table by email
5. **If user exists:**
   - Set `auth_provider_id` from WorkOS user ID if not already set
   - Set `external_id` in WorkOS to local user UUID
   - Check if local role matches WorkOS role; if mismatch, **update WorkOS to match local** (FlowRMS is source of truth)
6. **If user doesn't exist:**
   - Create new user in `PyUser.Users` with:
     - `email`: from WorkOS
     - `username`: defaults to email
     - `first_name`, `last_name`: from WorkOS profile
     - `role`: from WorkOS membership role
     - `auth_provider_id`: WorkOS user ID
     - `enabled`: `True`
   - Set `external_id` in WorkOS to newly created user UUID

### Tenant Resolution (Webhooks)

Since webhooks don't have JWT tokens, tenant resolution works differently:

1. Get WorkOS organization membership from user event
2. Extract `org_id` (WorkOS organization ID)
3. Look up `Tenant` record where `Tenant.org_id == workos_org_id`
4. Use `Tenant.url` as `tenant_name` for `MultiTenantController.scoped_session()`

### Key Integration Points

| WorkOS Field | Local Field | Notes |
|--------------|-------------|-------|
| User ID (`sub`) | `auth_provider_id` | WorkOS user identifier |
| `external_id` | `User.id` | Local UUID stored in WorkOS |
| Organization ID | `Tenant.org_id` | Maps org to tenant |
| Membership `role_slug` | `User.role` | Uses `RbacRoleEnum` |

### Configuration

**New environment variable required:**

```
WORKOS_WEBHOOK_SECRET=<secret from WorkOS dashboard>
```

Add `workos_webhook_secret` field to existing `WorkOSSettings` class (follows same pattern as `workos_api_key` and `workos_client_id`).

---

## Critical Files

| File | Purpose | Status |
|------|---------|--------|
| [`app/webhooks/__init__.py`](../../app/webhooks/__init__.py) | Webhooks module | Done |
| [`app/webhooks/workos/__init__.py`](../../app/webhooks/workos/__init__.py) | WorkOS webhook module | Done |
| [`app/webhooks/workos/router.py`](../../app/webhooks/workos/router.py) | FastAPI webhook endpoint | Done |
| [`app/webhooks/workos/services/__init__.py`](../../app/webhooks/workos/services/__init__.py) | Services module | Done |
| [`app/webhooks/workos/services/user_sync_service.py`](../../app/webhooks/workos/services/user_sync_service.py) | User sync business logic | Done |
| [`app/core/config/workos_settings.py`](../../app/core/config/workos_settings.py) | Add webhook secret | Done |
| [`app/admin/tenants/repositories/tenants_repository.py`](../../app/admin/tenants/repositories/tenants_repository.py) | Added `get_by_org_id` method | Done |
| [`app/api/app.py`](../../app/api/app.py) | Register webhook router | Done |
| [`app/core/providers.py`](../../app/core/providers.py) | Register UserSyncService provider | Done |
| [`app/webhooks/workos/providers.py`](../../app/webhooks/workos/providers.py) | Webhook providers | Done |
| [`tests/webhooks/workos/test_router.py`](../../tests/webhooks/workos/test_router.py) | Router tests | Done |
| [`tests/webhooks/workos/test_user_sync_service.py`](../../tests/webhooks/workos/test_user_sync_service.py) | Service tests | Done |

---

## Phase 1: Webhook Infrastructure

_Set up the FastAPI webhook endpoint and WorkOS event parsing._

### 1.1 RED: Write failing tests for webhook endpoint

**Test scenarios:**
- `test_webhook_rejects_missing_signature` - Returns 401 when WorkOS-Signature header missing
- `test_webhook_rejects_invalid_signature` - Returns 401 for invalid signature
- `test_webhook_accepts_valid_signature` - Returns 200 for valid signed request
- `test_webhook_parses_user_created_event` - Correctly parses user.created event and calls service
- `test_webhook_ignores_non_user_created_events` - Returns 200 but doesn't call service for other events

### 1.2 GREEN: Implement webhook endpoint

**Files created:**
- [`app/webhooks/__init__.py`](../../app/webhooks/__init__.py)
- [`app/webhooks/workos/__init__.py`](../../app/webhooks/workos/__init__.py)
- [`app/webhooks/workos/router.py`](../../app/webhooks/workos/router.py)
- [`app/webhooks/workos/services/__init__.py`](../../app/webhooks/workos/services/__init__.py)
- [`app/webhooks/workos/services/user_sync_service.py`](../../app/webhooks/workos/services/user_sync_service.py) (stub)
- [`tests/webhooks/__init__.py`](../../tests/webhooks/__init__.py)
- [`tests/webhooks/workos/__init__.py`](../../tests/webhooks/workos/__init__.py)
- [`tests/webhooks/workos/test_router.py`](../../tests/webhooks/workos/test_router.py)

**Files modified:**
- [`app/core/config/workos_settings.py`](../../app/core/config/workos_settings.py) - Added `workos_webhook_secret` field

**Implementation:**
- Signature verification using `workos.webhooks.Webhooks.verify_event()`
- Uses `Annotated[str | None, Header(...)]` pattern for type safety
- Dispatches to `UserSyncService.handle_user_created()` for user.created events

### 1.3 REFACTOR: Clean up and verify

- `task all` passes (lint, typecheck, tests)

---

## Phase 2: User Sync Service

_Implement the business logic for syncing users on creation._

### 2.1 RED: Write failing tests for user sync service

**Test scenarios:**
- `test_skip_if_external_id_exists` - No action if WorkOS user has external_id
- `test_skip_if_no_organization` - No action if WorkOS user has no org membership
- `test_skip_if_tenant_not_found` - No action if WorkOS org_id doesn't map to a tenant
- `test_link_existing_user_by_email` - Sets auth_provider_id and external_id on existing user
- `test_sync_role_to_workos_if_mismatch` - Updates WorkOS role when local role differs (FlowRMS is source of truth)
- `test_create_new_user_if_not_exists` - Creates user with WorkOS role, username=email, enabled=true

### 2.2 GREEN: Implement user sync service

**File:** [`app/webhooks/workos/services/user_sync_service.py`](../../app/webhooks/workos/services/user_sync_service.py)

**Dependencies:**
- `TenantsRepository` (existing - added `get_by_org_id` method)
- `MultiTenantController` (for tenant DB access)
- `WorkOSAuthService` (existing - for updating WorkOS user/membership)

**Methods:**
- `handle_user_created(event: UserCreatedWebhook) -> None` - Main handler
- `_get_first_organization_membership(user_id: str)` - Get first org membership
- `_find_user_by_email(session: AsyncSession, email: str) -> User | None`
- `_sync_existing_user(session, local_user, workos_user_id, membership) -> None`
- `_create_new_user(session, workos_user, membership) -> User`

### 2.3 REFACTOR: Clean up and verify

- Router updated to use aioinject's `@inject` decorator with `Injected[UserSyncService]`
- Router tests updated to use aioinject container with mocked service
- `task all` passes (lint, typecheck)
- All 11 tests pass (5 router + 6 service)

---

## Phase 3: Application Integration

_Wire up the webhook handler to the application._

### 3.1 GREEN: Register webhook router and providers

**Files created:**
- [`app/webhooks/workos/providers.py`](../../app/webhooks/workos/providers.py) - Webhook providers with `UserSyncService`

**Files modified:**
- [`app/api/app.py`](../../app/api/app.py) - Include webhooks router with prefix `/webhooks/workos`
- [`app/core/providers.py`](../../app/core/providers.py) - Register webhook providers

**Router registration:**
- Mount under `/webhooks/workos` path
- No authentication middleware (webhooks use signature verification)

### 3.2 VERIFY: Run task all

- All checks pass (lint, typecheck, tests)

---

## Phase 4: Verification

_Manual testing and final verification._

### 4.1 Manual testing

Tested webhook endpoint at `http://localhost:8006/webhooks/workos/` with sample payloads:

| Test | Scenario | Result |
|------|----------|--------|
| 1 | User with external_id | Skipped, returned 200 |
| 2 | User without org membership | Skipped, returned 200 |
| 3 | Non user.created event | Ignored, returned 200 |
| 4 | Missing signature | Rejected 401 |
| 5 | Invalid signature | Rejected 401 |

### 4.2 Final verification

- Run `task all` - All checks pass
- 11 webhook tests pass (5 router + 6 service)

---

## Changes During Review

_Issues identified during PR review and fixed. Prefixes: BF = bugfix, CH = behavior change._

### CH-1: Add missing type hints

**Problem**: Several functions missing type annotations for WorkOS SDK types
**Files**: [`app/webhooks/workos/services/user_sync_service.py`](../../app/webhooks/workos/services/user_sync_service.py)
**Changes**:
- Added return type `OrganizationMembership | None` to `_get_first_organization_membership`
- Added `OrganizationMembership` type hint to `membership` parameter in `_sync_existing_user`
- Added `WorkOSUser` and `OrganizationMembership` type hints to `_create_new_user`

### CH-2: Replace type: ignore with cast

**Problem**: `type: ignore[arg-type]` comment suppressing type error on line 56
**File**: [`app/webhooks/workos/services/user_sync_service.py`](../../app/webhooks/workos/services/user_sync_service.py)
**Change**: Replaced with `cast(str, tenant.url)` for explicit type conversion

### CH-3: Use specific exception in webhook router

**Problem**: Broad `except Exception` clause catching all exceptions
**File**: [`app/webhooks/workos/router.py`](../../app/webhooks/workos/router.py)
**Change**: Changed to `except ValueError` since WorkOS SDK raises `ValueError` for signature verification failures

### CH-4: Extract repository from service — bypass of repository pattern

**Problem**: `user_sync_service.py` performs direct SQLAlchemy queries (`select`, `session.add`, `session.flush`) in `_find_user_by_email`, `_sync_existing_user`, and `_create_new_user`. This violates SRP — services should orchestrate business logic, not access the DB directly.
**Review**: PR #172 review by marshallflowrms (2026-02-04)
**Files**: [`app/webhooks/workos/services/user_sync_service.py`](../../app/webhooks/workos/services/user_sync_service.py)
**Change**: Create a `WebhookUserRepository` that accepts only `AsyncSession` (since webhooks lack JWT/AuthInfo), with `get_by_email`, `create`, and `update` methods. Inject it into the service to replace inline DB operations.

### CH-5: Separate external API calls from DB transaction

**Problem**: In `handle_user_created`, WorkOS API calls (`update_user`, `update_organization_membership`) are made inside a `session.begin()` block. If a later API call fails, the DB transaction rolls back but earlier WorkOS changes persist — leaving systems in an inconsistent state.
**Review**: PR #172 review by marshallflowrms (2026-02-04)
**Files**: [`app/webhooks/workos/services/user_sync_service.py`](../../app/webhooks/workos/services/user_sync_service.py)
**Change**: Persist DB changes first, then perform WorkOS API calls outside the transaction with explicit error handling for partial failures.

### CH-6: Test real user creation logic instead of mocking private method

**Problem**: `test_create_new_user_if_not_exists` replaces `_create_new_user` with a mock, so the actual user creation logic (User model instantiation, field assignments, `WORKOS_ROLE_TO_RBAC` mapping) is untested.
**Review**: PR #172 review by marshallflowrms (2026-02-04)
**Files**: [`tests/webhooks/workos/test_user_sync_service.py`](../../tests/webhooks/workos/test_user_sync_service.py)
**Change**: Rewrite the test to exercise the real `_create_new_user` method, mocking only external dependencies (session, WorkOS client), and assert correct field mapping and role assignment.

### REC-1: Inject WorkOSSettings via DI (recommendation)

**Problem**: Router uses `@functools.cache` on `get_workos_settings()` to load settings. While this follows the existing pattern in `o365_router.py`, the router already uses aioinject's `@inject`, and `WorkOSSettings` is registered in the DI container.
**Review**: PR #172 review by marshallflowrms (2026-02-04)
**Files**: [`app/webhooks/workos/router.py`](../../app/webhooks/workos/router.py)
**Change**: Optional — inject `WorkOSSettings` via `Injected[WorkOSSettings]` instead of `@functools.cache` for consistency within the file.

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 3 days |
| Phases | 4 |
| Files Modified | 15 |
| Tests Added | 11 |
