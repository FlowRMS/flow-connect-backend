# User Organization Query

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1544](https://linear.app/flow-labs/issue/FLO-1544/create-a-query-to-get-the-user-organization-data)
- **Created**: 2026-02-04 08:47 -03
- **Approved**: 2026-02-04 09:57 -03
- **Finished**: 2026-02-04 14:16 -03
- **PR**: [#33](https://github.com/FlowRMS/flow-py-connect/pull/33)
- **Commit Prefix**: User Organization Query

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: GraphQL Response Type](#phase-1-graphql-response-type)
- [Phase 2: Service Layer (TDD)](#phase-2-service-layer-tdd)
- [Phase 3: GraphQL Query & Schema Integration](#phase-3-graphql-query--schema-integration)
- [Phase 4: Verification](#phase-4-verification)
- [Review](#review)
- [Results](#results)

---

## Overview

Create a GraphQL query that returns the authenticated user's organization data, specifically the organization type (`org_type`). The query resolves the user's primary organization from their auth context and returns core organization fields.

**GraphQL query**: `userOrganization` (no parameters - uses auth context)

**Data flow**: `AuthInfo.auth_provider_id` (WorkOS user ID) → `RemoteUser.org_primary_id` → `RemoteOrg`

---

## Design Decisions

### DD-1: Dedicated service vs reusing OrganizationSearchService

**Decision**: Create a dedicated `UserOrganizationService` rather than extending `OrganizationSearchService`.

- `OrganizationSearchService` is focused on search/connection logic with many dependencies (PosContactRepository, ConnectionService, AgreementService, TerritoryRepository)
- The user organization query is simple coordination: resolve user → fetch org
- A focused service follows the Single Responsibility Principle (SRP)
- Only needs `UserOrgRepository` + `OrganizationSearchRepository` + `AuthInfo`

### DD-2: Response type design

**Decision**: Create a minimal `UserOrganizationResponse` with core org fields, not reuse `OrganizationLiteResponse`.

- `OrganizationLiteResponse` includes connection-specific data (pos_contacts, connection_status, agreement, subdivisions) that are irrelevant for the user's own org
- A focused response type avoids unnecessary data fetching and keeps the query lightweight
- Fields: `id`, `name`, `org_type`, `domain`

### DD-3: Register OrgType as Strawberry enum

**Decision**: Register `OrgType` as a Strawberry enum for type-safe GraphQL schema.

- Currently only `ConnectionStatus` is registered as a Strawberry enum
- Using enums in the GraphQL schema provides better client-side type safety
- Registration follows the same pattern: `strawberry.enum(OrgType)` in the types file

---

## Critical Files

| File | Action | Description |
|------|--------|-------------|
| [`app/graphql/organizations/strawberry/user_organization_types.py`](../../app/graphql/organizations/strawberry/user_organization_types.py) | **Create** ✅ | `UserOrganizationResponse` type |
| [`app/graphql/organizations/services/user_organization_service.py`](../../app/graphql/organizations/services/user_organization_service.py) | **Create** ✅ | Service to get user's org |
| [`app/graphql/organizations/queries/user_organization_queries.py`](../../app/graphql/organizations/queries/user_organization_queries.py) | **Create** ✅ | GraphQL query resolver |
| [`app/graphql/organizations/queries/__init__.py`](../../app/graphql/organizations/queries/__init__.py) | **Modify** ✅ | Export new query class |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | **Modify** ✅ | Register query in schema |
| [`tests/graphql/organizations/services/test_user_organization_service.py`](../../tests/graphql/organizations/services/test_user_organization_service.py) | **Create** ✅ | Service tests |
| [`schema.graphql`](../../schema.graphql) | **Modify** ✅ | Updated schema (auto-generated) |

---

## Phase 1: GraphQL Response Type

_Create the `UserOrganizationResponse` Strawberry type and register org enums._

### 1.1 GREEN: Create UserOrganizationResponse type ✅

**File**: [`app/graphql/organizations/strawberry/user_organization_types.py`](../../app/graphql/organizations/strawberry/user_organization_types.py)

- Register `OrgType` as Strawberry enum
- Create `UserOrganizationResponse` with fields:
  - `id: strawberry.ID`
  - `name: str`
  - `org_type: OrgType`
  - `domain: str | None`
- Add `from_orm_model(org: RemoteOrg)` static method for conversion

### 1.2 VERIFY: Run `task all` ✅

---

## Phase 2: Service Layer (TDD)

_Create `UserOrganizationService` to resolve the authenticated user's organization._

### 2.1 RED: Write failing tests for UserOrganizationService ✅

**File**: [`tests/graphql/organizations/services/test_user_organization_service.py`](../../tests/graphql/organizations/services/test_user_organization_service.py)

**Test scenarios**:
- `test_get_user_organization_returns_org` - Returns the user's org when found
- `test_get_user_organization_user_not_found` - Raises `UserNotFoundError` when WorkOS user ID doesn't exist
- `test_get_user_organization_no_primary_org` - Raises `UserOrganizationRequiredError` when user has no primary org
- `test_get_user_organization_org_not_found` - Raises error when org_id exists but org is deleted/missing
- `test_get_user_organization_no_auth_provider_id` - Raises error when auth_provider_id is None

### 2.2 GREEN: Implement UserOrganizationService ✅

**File**: [`app/graphql/organizations/services/user_organization_service.py`](../../app/graphql/organizations/services/user_organization_service.py)

- Constructor injects: `UserOrgRepository`, `OrganizationSearchRepository`, `AuthInfo`
- `get_user_organization() -> RemoteOrg` method:
  1. Get `auth_provider_id` from `AuthInfo`
  2. Call `UserOrgRepository.get_user_org_id(auth_provider_id)` to get org UUID
  3. Call `OrganizationSearchRepository.get_by_id(org_id)` to fetch the org
  4. Raise error if org not found
  5. Return the org

### 2.3 REFACTOR: Clean up ✅

### 2.4 VERIFY: Run `task all` ✅

---

## Phase 3: GraphQL Query & Schema Integration

_Create the query resolver and register it in the schema._

### 3.1 GREEN: Create UserOrganizationQueries ✅

**File**: [`app/graphql/organizations/queries/user_organization_queries.py`](../../app/graphql/organizations/queries/user_organization_queries.py)

- `@strawberry.type` class with a `user_organization` field
- Injects `UserOrganizationService`
- Calls `service.get_user_organization()` and converts to `UserOrganizationResponse`

### 3.2 GREEN: Register in schema ✅

- Update [`app/graphql/organizations/queries/__init__.py`](../../app/graphql/organizations/queries/__init__.py) to export `UserOrganizationQueries`
- Update [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) to add `UserOrganizationQueries` to `Query` bases
- Export updated [`schema.graphql`](../../schema.graphql)

### 3.3 VERIFY: Run `task all` ✅

---

## Phase 4: Verification

_Manual testing to verify the query works end-to-end._

### 4.1 Manual Testing ✅

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Query `userOrganization` with valid auth | Returns org data with `orgType` field | ✅ |
| 2 | Verify `orgType` returns correct enum value | One of: MANUFACTURER, DISTRIBUTOR, REP_FIRM, ASSOCIATION, ADMIN_ORG | ✅ `REP_FIRM` |
| 3 | Schema introspection for `UserOrganizationResponse` type | Type exists with all fields | ✅ `id`, `name`, `orgType`, `domain` |
| 4 | Schema introspection for `OrgType` enum | Enum values visible | ✅ 5 values |

---

## Changes During Testing

_Issues discovered and fixed during testing/review. Prefixes: BF = bugfix, CH = behavior change._

### BF-1: ExchangeFileService fixture missing validation_issue_repository ✅

**Problem**: `ExchangeFileService.__init__()` was updated to require `validation_issue_repository` but the test fixture in `TestGetSentFilesGroupedService` was not updated, causing 3 test errors.
**File**: [`tests/graphql/pos/data_exchange/test_sent_exchange_files.py`](../../tests/graphql/pos/data_exchange/test_sent_exchange_files.py)
**Fix**: Added `mock_validation_issue_repository` fixture and passed it to the service constructor.

### BF-2: FileValidationIssueResponse title assertion uses wrong column_name ✅

**Problem**: Test used `column_name="quantity"` which doesn't match any entry in `ISSUE_TITLE_MAPPING`, causing the title fallback to generate `"Required Field validation issue"` instead of the expected `"Quantity missing"`.
**File**: [`tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py`](../../tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py)
**Fix**: Changed `column_name` to `"quantity_units_sold"` which is the correct column mapped to `"Quantity missing"` in the title mapping.

### CH-1: Removed ORGS_DB_URL guard clause from UserOrganizationQueries ✅

**Problem**: Initial implementation included a guard clause returning `None` if `ORGS_DB_URL` env var was not set (following `ConnectionQueries` pattern). User feedback: prefer explicit failure since `ORGS_DB_URL` is temporary.
**File**: [`app/graphql/organizations/queries/user_organization_queries.py`](../../app/graphql/organizations/queries/user_organization_queries.py)
**Change**: Removed the `ORGS_DB_URL` guard clause. Query now requires the env var to be set and will fail explicitly if missing. Return type changed from `UserOrganizationResponse | None` to `UserOrganizationResponse`.

### CH-2: Removed status field from UserOrganizationResponse ✅

**Problem**: Initial design included `status: OrgStatus | None` field and registered `OrgStatus` as a Strawberry enum. User feedback: status is always ACTIVE for authenticated users, so it's unnecessary.
**File**: [`app/graphql/organizations/strawberry/user_organization_types.py`](../../app/graphql/organizations/strawberry/user_organization_types.py)
**Change**: Removed `status` field from `UserOrganizationResponse` and removed `OrgStatus` Strawberry enum registration.

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns — read-only query, two simple DB lookups |
| 2 | Effects on other features | ✅ No negative effects — additive query, no existing code modified |
| 3 | Code quality issues | ✅ Clean — small focused files, follows existing patterns |
| 4 | Potential bugs | ✅ None found — all error paths covered by tests |
| 5 | Commit messages | ✅ Single-line, correct `[Prefix] - Phase N - Description` format |
| 6 | No Co-Authored-By | ✅ None found in any of the 6 commits |
| 7 | Document updates | ✅ All phases marked ✅, critical files linked, CH entries documented |

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~5h 30m |
| Phases | 4 |
| Files Modified | 12 |
| Tests Added | 5 |
