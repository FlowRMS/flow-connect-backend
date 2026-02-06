# Manufacturer Aliases

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1187](https://linear.app/flow-labs/issue/FLO-1187/flowpos-manufacturer-aliases)
- **Created**: 2026-01-22 08:34 -03
- **Approved**: 2026-01-22 08:55 -03
- **Finished**: 2026-01-22 11:25 -03
- **PR**: [#14](https://github.com/FlowRMS/flow-py-connect/pull/14)
- **Commit Prefix**: Organization Aliases

---

## Table of Contents

- [Overview](#overview)
- [Validation Rules](#validation-rules)
- [Design Pattern](#design-pattern)
- [Critical Files](#critical-files)
- [Phase 1: DB Schema](#phase-1-db-schema)
- [Phase 2: Repository Layer](#phase-2-repository-layer)
- [Phase 3: Service Layer](#phase-3-service-layer)
- [Phase 4: GraphQL Layer](#phase-4-graphql-layer)
- [Phase 5: Verification](#phase-5-verification-)
- [Changes During Testing](#changes-during-testing)
- [Results](#results)

---

## Overview

Implement manufacturer aliases - different names that users can assign to connected manufacturers. Each organization can assign multiple aliases to different manufacturers.

### GraphQL Operations

| Operation | Type | Description |
|-----------|------|-------------|
| `createManufacturerAlias` | Mutation | Create a single alias |
| `deleteManufacturerAlias` | Mutation | Delete an alias by ID |
| `bulkSpreadsheetCreateManufacturerAliases` | Mutation | Bulk create from CSV file |
| `manufacturerAliasSearch` | Query | Return all aliases grouped by connected org |

### Bulk CSV Format

| Column | Required | Description |
|--------|----------|-------------|
| Organization Name | Yes | Name of the organization (case-insensitive match) |
| Alias | Yes | The alias to assign |

### Bulk Response

- `inserted_count`: Number of successfully created aliases
- `failures`: List of failures with row number and reason:
  - Organization not found
  - Alias already exists
  - Missing alias value

---

## Validation Rules

1. **Connection Required**: The connected organization must have `ConnectionStatus = ACCEPTED`
2. **Case-Insensitive Uniqueness**: Alias must be unique per user's organization (case-insensitive)
3. **Organization Scope**: Members of the same organization cannot duplicate aliases for the same connected org
4. **Cross-Organization**: Different organizations CAN have the same alias for the same connected org
5. **Strict CSV Columns**: Column names must match exactly: "Organization Name", "Alias"

---

## Design Pattern

**Repository Pattern** - *Martin Fowler, Patterns of Enterprise Application Architecture (2003)*

> "Mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects."

**Application**: `OrganizationAliasRepository` abstracts all data access for aliases, while `OrganizationAliasService` handles business logic (validation, bulk processing).

---

## Critical Files

| File | Action | Description |
|------|--------|-------------|
| [`alembic/versions/20260122_create_organization_aliases.py`](../../alembic/versions/20260122_create_organization_aliases.py) | ✅ | Database migration |
| [`app/graphql/pos/organization_alias/models/organization_alias.py`](../../app/graphql/pos/organization_alias/models/organization_alias.py) | ✅ | SQLAlchemy model |
| [`app/graphql/pos/organization_alias/repositories/organization_alias_repository.py`](../../app/graphql/pos/organization_alias/repositories/organization_alias_repository.py) | ✅ | Data access layer |
| [`app/graphql/pos/organization_alias/services/organization_alias_service.py`](../../app/graphql/pos/organization_alias/services/organization_alias_service.py) | ✅ | Core service (CRUD + validation) |
| [`app/graphql/pos/organization_alias/services/organization_alias_bulk_service.py`](../../app/graphql/pos/organization_alias/services/organization_alias_bulk_service.py) | ✅ | Bulk import service |
| [`app/graphql/pos/organization_alias/services/organization_alias_csv_parser.py`](../../app/graphql/pos/organization_alias/services/organization_alias_csv_parser.py) | ✅ | CSV parsing |
| [`app/graphql/pos/organization_alias/exceptions.py`](../../app/graphql/pos/organization_alias/exceptions.py) | ✅ | Domain exceptions |
| [`app/graphql/pos/organization_alias/strawberry/organization_alias_types.py`](../../app/graphql/pos/organization_alias/strawberry/organization_alias_types.py) | ✅ | GraphQL response types |
| [`app/graphql/pos/organization_alias/strawberry/organization_alias_inputs.py`](../../app/graphql/pos/organization_alias/strawberry/organization_alias_inputs.py) | ✅ | GraphQL input types |
| [`app/graphql/pos/organization_alias/mutations/organization_alias_mutations.py`](../../app/graphql/pos/organization_alias/mutations/organization_alias_mutations.py) | ✅ | GraphQL mutations |
| [`app/graphql/pos/organization_alias/queries/organization_alias_queries.py`](../../app/graphql/pos/organization_alias/queries/organization_alias_queries.py) | ✅ | GraphQL queries |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | ✅ | Register queries/mutations |

---

## Phase 1: DB Schema

*Create the database model and migration for manufacturer aliases.*

### 1.1 GREEN: Create Migration ✅

**File**: [`alembic/versions/20260122_create_organization_aliases.py`](../../alembic/versions/20260122_create_organization_aliases.py)

**Table**: `organization_aliases` in `connect_pos` schema

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `organization_id` | UUID | Not Null (user's org) |
| `connected_org_id` | UUID | Not Null (manufacturer org) |
| `alias` | String(255) | Not Null |
| `created_at` | Timestamp(tz) | Server Default now() |
| `created_by_id` | UUID | Not Null |

**Constraints**:
- `uq_organization_aliases_org_connected`: Unique on `(organization_id, connected_org_id)` - one alias per manufacturer per org
- `uq_organization_aliases_org_alias_lower`: Unique on `(organization_id, LOWER(alias))` - case-insensitive alias uniqueness per org
- Index on `organization_id` for efficient queries

Revision: `20260122_001`, depends on `20260121_001`

### 1.2 GREEN: Create SQLAlchemy Model ✅

**File**: [`app/graphql/pos/organization_alias/models/organization_alias.py`](../../app/graphql/pos/organization_alias/models/organization_alias.py)

Model using `PyConnectPosBaseModel`, `HasCreatedBy`, `HasCreatedAt` mixins.

Fields:
- `organization_id: Mapped[uuid.UUID]` - User's organization
- `connected_org_id: Mapped[uuid.UUID]` - Manufacturer organization
- `alias: Mapped[str]` - The alias string

### 1.3 VERIFY ✅

Run `task all` - verify type checks and linting pass.

---

## Phase 2: Repository Layer

*Implement the data access layer for manufacturer aliases.*

### 2.1 RED: Write Repository Tests ✅

**File**: [`tests/graphql/pos/organization_alias/repositories/test_organization_alias_repository.py`](../../tests/graphql/pos/organization_alias/repositories/test_organization_alias_repository.py)

**Test scenarios**:
- `test_create_alias_returns_alias` - Creates and returns alias
- `test_get_by_id_returns_alias` - Returns alias by UUID
- `test_get_by_id_returns_none_for_missing` - Returns None when not found
- `test_get_by_org_and_connected_org` - Finds alias by org pair
- `test_get_all_by_org_returns_list` - Returns all aliases for user's org
- `test_alias_exists_case_insensitive_returns_true` - Case-insensitive existence check
- `test_alias_exists_returns_false_when_not_found` - Returns False when alias doesn't exist
- `test_delete_removes_alias` - Deletes alias and returns True

### 2.2 GREEN: Implement Repository ✅

**File**: [`app/graphql/pos/organization_alias/repositories/organization_alias_repository.py`](../../app/graphql/pos/organization_alias/repositories/organization_alias_repository.py)

Dependencies:
- `session: TenantSession` - For connect_pos schema
- `orgs_session: AsyncSession` - For subscription schema (orgs/connections)

Methods:
- `async def create(self, alias: OrganizationAlias) -> OrganizationAlias`
- `async def get_by_id(self, alias_id: uuid.UUID) -> OrganizationAlias | None`
- `async def get_by_org_and_connected_org(self, org_id: uuid.UUID, connected_org_id: uuid.UUID) -> OrganizationAlias | None`
- `async def get_all_by_org(self, org_id: uuid.UUID) -> list[OrganizationAlias]`
- `async def alias_exists(self, org_id: uuid.UUID, alias: str) -> bool` - Uses `func.lower()` for case-insensitive
- `async def delete(self, alias_id: uuid.UUID) -> bool`
- `async def get_connected_orgs_by_name(self, user_org_id: uuid.UUID, org_names: list[str]) -> dict[str, RemoteOrg]` - Batch lookup for bulk import

### 2.3 VERIFY ✅

Run `task all` - verify all tests pass.

---

## Phase 3: Service Layer

*Implement business logic for validation and bulk operations.*

### 3.1 RED: Write Core Service Tests ✅

**File**: [`tests/graphql/pos/organization_alias/services/test_organization_alias_service.py`](../../tests/graphql/pos/organization_alias/services/test_organization_alias_service.py)

**Test scenarios**:
- `test_create_alias_succeeds` - Creates alias for connected org
- `test_create_alias_fails_not_connected` - Raises `OrganizationNotConnectedError`
- `test_create_alias_fails_duplicate` - Raises `AliasAlreadyExistsError`
- `test_delete_alias_succeeds` - Deletes alias
- `test_delete_alias_fails_not_found` - Raises `OrganizationAliasNotFoundError`
- `test_get_all_aliases_grouped` - Returns aliases grouped by connected org

### 3.2 RED: Write Bulk Service Tests ✅

**File**: [`tests/graphql/pos/organization_alias/services/test_organization_alias_bulk_service.py`](../../tests/graphql/pos/organization_alias/services/test_organization_alias_bulk_service.py)

**Test scenarios**:
- `test_bulk_create_succeeds` - Creates multiple aliases (calls core service per row)
- `test_bulk_create_reports_org_not_found` - Reports "Organization not found"
- `test_bulk_create_reports_not_connected` - Reports "Organization not connected" (from core service exception)
- `test_bulk_create_reports_alias_exists` - Reports "Alias already exists" (from core service exception)
- `test_bulk_create_reports_missing_alias` - Reports "Missing alias value"
- `test_bulk_create_partial_success` - Some rows succeed, some fail, returns correct counts

### 3.3 GREEN: Create Exceptions ✅

**File**: [`app/graphql/pos/organization_alias/exceptions.py`](../../app/graphql/pos/organization_alias/exceptions.py)

Exception hierarchy:
- `OrganizationAliasError` - Base exception
  - `AliasAlreadyExistsError` - Alias already exists for org
  - `OrganizationNotConnectedError` - Target org not connected (ACCEPTED)
  - `OrganizationAliasNotFoundError` - Alias not found by ID
  - `CsvParseError` - CSV parsing failed
    - `InvalidCsvColumnsError` - CSV columns don't match expected

### 3.4 GREEN: Create CSV Parser ✅

**File**: [`app/graphql/pos/organization_alias/services/organization_alias_csv_parser.py`](../../app/graphql/pos/organization_alias/services/organization_alias_csv_parser.py)

Functions:
- `parse_csv(content: bytes) -> list[CsvRow]` - Parses CSV, validates columns
- `CsvRow` dataclass: `row_number: int, organization_name: str, alias: str`

Raises `InvalidCsvColumnsError` if columns don't match exactly.

### 3.5 GREEN: Implement Core Service ✅

**File**: [`app/graphql/pos/organization_alias/services/organization_alias_service.py`](../../app/graphql/pos/organization_alias/services/organization_alias_service.py)

Dependencies:
- `repository: OrganizationAliasRepository`
- `connection_repository: ConnectionRepository`
- `user_org_repository: UserOrgRepository`
- `auth_info: AuthInfo`

Methods:
- `async def create_alias(self, connected_org_id: uuid.UUID, alias: str) -> OrganizationAlias`
  1. Get user's org_id via `user_org_repository`
  2. Validate connection is ACCEPTED via `connection_repository`
  3. Validate alias uniqueness via `repository.alias_exists()`
  4. Create and return alias

- `async def delete_alias(self, alias_id: uuid.UUID) -> bool`
  1. Get alias by ID
  2. Verify it exists
  3. Delete and return True

- `async def get_all_aliases_grouped(self) -> list[AliasGroup]`
  1. Get user's org_id
  2. Get all aliases for org
  3. Group by connected_org_id
  4. Fetch org names for display

**Data classes**:
- `AliasGroup`: `connected_org_id: uuid.UUID, connected_org_name: str, aliases: list[OrganizationAlias]`

### 3.6 GREEN: Implement Bulk Service ✅

**File**: [`app/graphql/pos/organization_alias/services/organization_alias_bulk_service.py`](../../app/graphql/pos/organization_alias/services/organization_alias_bulk_service.py)

Dependencies:
- `alias_service: OrganizationAliasService` - Reuses validation logic
- `repository: OrganizationAliasRepository` - For batch org lookup by name

Methods:
- `async def bulk_create_from_csv(self, content: bytes) -> BulkCreateResult`
  1. Parse CSV (validates columns)
  2. Batch lookup organizations by name via `repository.get_connected_orgs_by_name()`
  3. For each row:
     - If org not found → record failure "Organization not found"
     - If alias missing → record failure "Missing alias value"
     - Otherwise → call `alias_service.create_alias(org_id, alias)`
       - Catches `OrganizationNotConnectedError` → record failure "Organization not connected"
       - Catches `AliasAlreadyExistsError` → record failure "Alias already exists"
       - Success → increment count
  4. Return `BulkCreateResult`

**Key design**: All validation logic lives in `OrganizationAliasService.create_alias()`. The bulk service only handles CSV parsing, org name resolution, and error collection. No validation duplication.

**Data classes**:
- `BulkCreateResult`: `inserted_count: int, failures: list[BulkFailure]`
- `BulkFailure`: `row_number: int, organization_name: str, alias: str, reason: str`

### 3.7 VERIFY ✅

Run `task all` - verify all tests pass.

---

## Phase 4: GraphQL Layer

*Implement GraphQL types, mutations, and queries.*

### 4.1 RED: Write GraphQL Tests ✅

**File**: [`tests/graphql/pos/organization_alias/mutations/test_organization_alias_mutations.py`](../../tests/graphql/pos/organization_alias/mutations/test_organization_alias_mutations.py)

**Test scenarios**:
- `test_create_alias_mutation` - Creates single alias
- `test_delete_alias_mutation` - Deletes alias
- `test_bulk_create_mutation` - Processes CSV

**File**: [`tests/graphql/pos/organization_alias/queries/test_organization_alias_queries.py`](../../tests/graphql/pos/organization_alias/queries/test_organization_alias_queries.py)

**Test scenarios**:
- `test_search_returns_grouped_aliases` - Returns aliases grouped by org

### 4.2 GREEN: Create Response Types ✅

**File**: [`app/graphql/pos/organization_alias/strawberry/organization_alias_types.py`](../../app/graphql/pos/organization_alias/strawberry/organization_alias_types.py)

Types to create:
- `OrganizationAliasResponse` - Single alias (id, connected_org_id, connected_org_name, alias, created_at)
- `OrganizationAliasGroupResponse` - Grouped by connected org (connected_org_id, connected_org_name, aliases list)
- `BulkCreateFailureResponse` - Single failure (row_number, organization_name, alias, reason)
- `BulkCreateOrganizationAliasesResponse` - Bulk result (inserted_count, failures list)

### 4.3 GREEN: Create Input Types ✅

**File**: [`app/graphql/pos/organization_alias/strawberry/organization_alias_inputs.py`](../../app/graphql/pos/organization_alias/strawberry/organization_alias_inputs.py)

Types to create:
- `CreateOrganizationAliasInput` - Input for single create (connected_org_id, alias)

### 4.4 GREEN: Implement Mutations ✅

**File**: [`app/graphql/pos/organization_alias/mutations/organization_alias_mutations.py`](../../app/graphql/pos/organization_alias/mutations/organization_alias_mutations.py)

Mutations:
- `create_organization_alias(input) -> OrganizationAliasResponse` - Uses `OrganizationAliasService`
- `delete_organization_alias(alias_id) -> bool` - Uses `OrganizationAliasService`
- `bulk_spreadsheet_create_organization_aliases(file) -> BulkCreateOrganizationAliasesResponse` - Uses `OrganizationAliasBulkService`

### 4.5 GREEN: Implement Query ✅

**File**: [`app/graphql/pos/organization_alias/queries/organization_alias_queries.py`](../../app/graphql/pos/organization_alias/queries/organization_alias_queries.py)

Queries:
- `organization_alias_search() -> list[OrganizationAliasGroupResponse]` - Uses `OrganizationAliasService`

### 4.6 GREEN: Register in Schema ✅

**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

- Add `OrganizationAliasQueries` to `Query` inheritance
- Add `OrganizationAliasMutations` to `Mutation` inheritance

### 4.7 VERIFY ✅

Run `task all` - verify all tests pass.

---

## Phase 5: Verification ✅

*Manual testing via GraphQL Playground.*

### 5.1 Test Create Alias ✅

1. ✅ Create alias for a connected organization
2. ✅ Verify error when organization not connected (ACCEPTED)
3. ✅ Verify error when alias already exists (case-insensitive)

### 5.2 Test Delete Alias ✅

1. ✅ Delete existing alias - verify returns true

### 5.3 Test Search ✅

1. ✅ Query aliases - verify grouped by connected org
2. ✅ Verify org names are included

### 5.4 Test Bulk Import

*(Skipped - requires file upload testing)*

---

## Changes During Testing

_Issues discovered and fixed during testing/review. Prefixes: BF = bugfix._

### BF-1: aioinject DI error with union types ✅

**Problem**: aioinject doesn't support union types like `AsyncSession | None` in constructor parameters, causing `'types.UnionType' object has no attribute '__name__'` error.

**File**: [`app/graphql/pos/organization_alias/repositories/organization_alias_repository.py`](../../app/graphql/pos/organization_alias/repositories/organization_alias_repository.py)

**Fix**: Changed `orgs_session: AsyncSession | None = None` to required parameter `orgs_session: AsyncSession`.

### BF-2: Missing org names in grouped aliases query ✅

**Problem**: `organizationAliases` query returned empty `connectedOrgName` because the service never fetched org names.

**Files**:
- [`organization_alias_repository.py`](../../app/graphql/pos/organization_alias/repositories/organization_alias_repository.py) - Added `get_org_names_by_ids()` method
- [`organization_alias_service.py`](../../app/graphql/pos/organization_alias/services/organization_alias_service.py) - Updated to fetch and populate org names

**Fix**: Added batch lookup of org names by IDs and populated `connectedOrgName` in grouped results.

### BF-3: Missing ownership check in delete (Security) ✅

**Problem**: `delete_alias` didn't verify the alias belongs to user's organization, allowing users to delete other orgs' aliases if they knew the UUID.

**Files**:
- [`organization_alias_service.py`](../../app/graphql/pos/organization_alias/services/organization_alias_service.py) - Added ownership validation
- [`test_organization_alias_service.py`](../../tests/graphql/pos/organization_alias/services/test_organization_alias_service.py) - Added test case

**Fix**: Added ownership check: `existing.organization_id != user_org_id`. Applied using TDD (RED → GREEN).

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~3 hours |
| Phases | 5 |
| Files Modified | 32 |
| Tests Added | 10 |
