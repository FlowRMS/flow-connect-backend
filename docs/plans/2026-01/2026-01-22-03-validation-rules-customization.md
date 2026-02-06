# Validation Rules - Customization Options

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1196](https://linear.app/flow-labs/issue/FLO-1196/flowpos-validation-rules-customization-options)
- **Created**: 2026-01-22 13:52 -03
- **Approved**: 2026-01-22 14:09 -03
- **Finished**: 2026-01-22 16:28 -03
- **PR**: [#16](https://github.com/FlowRMS/flow-py-connect/pull/16)
- **Commit Prefix**: Validation Rules

---

## Table of Contents

- [Overview](#overview)
- [Critical Files](#critical-files)
- [Phase 1: Database Schema](#phase-1-database-schema)
- [Phase 2: Repository & Service](#phase-2-repository--service)
- [Phase 3: GraphQL Layer](#phase-3-graphql-layer)
- [Phase 4: Organization Preference](#phase-4-organization-preference)
- [Phase 5: Verification](#phase-5-verification)
- [Results](#results)

---

## Overview

This plan implements the "Validation Rules - Customization Options" feature for the FlowPOS domain. It introduces:

1. **New Package**: `validations` in the `pos` domain
2. **Prefix Patterns Entity**: Organization-scoped list of patterns used for manufacturer part number prefix removal
   - Fields: `name` (mandatory), `description` (optional)
   - Organization-scoped: users can only see/manage their own organization's patterns
3. **Organization Preference**: "Manufacturer Part Number Prefix Removal" (boolean)

### Architecture Decision

**Pattern Reference**: Repository Pattern + Service Layer (Martin Fowler, Patterns of Enterprise Application Architecture)

Following the existing `organization_alias` package structure in the `pos` domain:
- Model with `organization_id` for multi-tenant scoping
- Repository with explicit organization filtering
- Service with `AuthInfo` for ownership validation
- GraphQL resolvers with `@inject` dependency injection

---

## Critical Files

| Category | File | Status |
|----------|------|--------|
| **Model** | [`app/graphql/pos/validations/models/prefix_pattern.py`](../../app/graphql/pos/validations/models/prefix_pattern.py) | ✅ |
| **Migration** | [`alembic/versions/20260122_create_prefix_patterns.py`](../../alembic/versions/20260122_create_prefix_patterns.py) | ✅ |
| **Repository** | [`app/graphql/pos/validations/repositories/prefix_pattern_repository.py`](../../app/graphql/pos/validations/repositories/prefix_pattern_repository.py) | ✅ |
| **Service** | [`app/graphql/pos/validations/services/prefix_pattern_service.py`](../../app/graphql/pos/validations/services/prefix_pattern_service.py) | ✅ |
| **Types** | [`app/graphql/pos/validations/strawberry/prefix_pattern_types.py`](../../app/graphql/pos/validations/strawberry/prefix_pattern_types.py) | ✅ |
| **Inputs** | [`app/graphql/pos/validations/strawberry/prefix_pattern_inputs.py`](../../app/graphql/pos/validations/strawberry/prefix_pattern_inputs.py) | ✅ |
| **Queries** | [`app/graphql/pos/validations/queries/prefix_pattern_queries.py`](../../app/graphql/pos/validations/queries/prefix_pattern_queries.py) | ✅ |
| **Mutations** | [`app/graphql/pos/validations/mutations/prefix_pattern_mutations.py`](../../app/graphql/pos/validations/mutations/prefix_pattern_mutations.py) | ✅ |
| **Exceptions** | [`app/graphql/pos/validations/exceptions.py`](../../app/graphql/pos/validations/exceptions.py) | ✅ |
| **Preference Enum** | [`app/graphql/pos/preferences/enums.py`](../../app/graphql/pos/preferences/enums.py) | ✅ |
| **Preference Config** | [`app/graphql/pos/preferences/config.py`](../../app/graphql/pos/preferences/config.py) | ✅ |
| **Tests - Repository** | [`tests/graphql/pos/validations/repositories/test_prefix_pattern_repository.py`](../../tests/graphql/pos/validations/repositories/test_prefix_pattern_repository.py) | ✅ |
| **Tests - Service** | [`tests/graphql/pos/validations/services/test_prefix_pattern_service.py`](../../tests/graphql/pos/validations/services/test_prefix_pattern_service.py) | ✅ |
| **Tests - Queries** | [`tests/graphql/pos/validations/queries/test_prefix_pattern_queries.py`](../../tests/graphql/pos/validations/queries/test_prefix_pattern_queries.py) | ✅ |
| **Tests - Mutations** | [`tests/graphql/pos/validations/mutations/test_prefix_pattern_mutations.py`](../../tests/graphql/pos/validations/mutations/test_prefix_pattern_mutations.py) | ✅ |

---

## Phase 1: Database Schema

Create the database model and migration for the `prefix_patterns` table.

### 1.1 GREEN: Create PrefixPattern model ✅

**File**: `app/graphql/pos/validations/models/prefix_pattern.py`

Model definition:
- Inherits from `PyConnectPosBaseModel`, `HasCreatedBy`, `HasCreatedAt`
- Table name: `prefix_patterns`
- Schema: `connect_pos`
- Fields:
  - `organization_id: Mapped[uuid.UUID]` - FK to organizations (nullable=False)
  - `name: Mapped[str]` - String(100), nullable=False
  - `description: Mapped[str | None]` - String(500), nullable=True
- Relationship: `created_by: Mapped[User]`
- Unique constraint: `(organization_id, name)` - prevent duplicate names per org

Also create:
- `app/graphql/pos/validations/__init__.py`
- `app/graphql/pos/validations/models/__init__.py` - export `PrefixPattern`

### 1.2 GREEN: Create Alembic migration ✅

**File**: `alembic/versions/20260122_create_prefix_patterns.py`

Migration:
- Create `connect_pos.prefix_patterns` table with all columns
- Add unique constraint `uq_prefix_patterns_org_name`
- Add index on `organization_id` for query performance
- Downgrade: drop table

### 1.3 VERIFY: Run `task all` ✅

---

## Phase 2: Repository & Service

Implement data access and business logic layers following TDD.

### 2.1 RED: Write failing tests for repository ✅

**File**: `tests/graphql/pos/validations/repositories/test_prefix_pattern_repository.py`

**Test scenarios**:
- `test_create_prefix_pattern` - Creates and returns pattern with generated ID
- `test_get_by_id_returns_pattern` - Fetches existing pattern by ID
- `test_get_by_id_returns_none_when_not_found` - Returns None for non-existent ID
- `test_get_all_by_org_returns_patterns` - Returns all patterns for an organization
- `test_delete_removes_pattern` - Deletes pattern and returns True
- `test_delete_returns_false_when_not_found` - Returns False for non-existent ID
- `test_exists_by_org_and_name_returns_true` - Returns True when pattern with name exists in org
- `test_exists_by_org_and_name_returns_false` - Returns False when pattern doesn't exist

Also create:
- `tests/graphql/pos/validations/__init__.py`
- `tests/graphql/pos/validations/repositories/__init__.py`

### 2.2 GREEN: Implement repository ✅

**File**: `app/graphql/pos/validations/repositories/prefix_pattern_repository.py`

Class: `PrefixPatternRepository`

Constructor:
- `session: TenantSession`

Methods:
- `async def create(self, pattern: PrefixPattern) -> PrefixPattern`
- `async def get_by_id(self, pattern_id: uuid.UUID) -> PrefixPattern | None`
- `async def get_all_by_org(self, org_id: uuid.UUID) -> list[PrefixPattern]`
- `async def delete(self, pattern_id: uuid.UUID) -> bool`
- `async def exists_by_org_and_name(self, org_id: uuid.UUID, name: str) -> bool`

Also create:
- `app/graphql/pos/validations/repositories/__init__.py` - export `PrefixPatternRepository`

### 2.3 RED: Write failing tests for service ✅

**File**: `tests/graphql/pos/validations/services/test_prefix_pattern_service.py`

**Test scenarios**:
- `test_create_pattern_success` - Creates pattern with name and optional description
- `test_create_pattern_sets_created_by_id` - Sets created_by_id from auth_info
- `test_create_pattern_duplicate_name_raises_error` - Raises error when name exists in org
- `test_create_pattern_unauthenticated_raises_error` - Raises error when user not authenticated
- `test_get_all_patterns_returns_org_patterns` - Returns all patterns for user's org
- `test_delete_pattern_success` - Deletes pattern owned by user's org
- `test_delete_pattern_not_found_raises_error` - Raises error when pattern doesn't exist
- `test_delete_pattern_wrong_org_raises_error` - Raises error when trying to delete another org's pattern

Also create:
- `tests/graphql/pos/validations/services/__init__.py`

### 2.4 GREEN: Implement service and exceptions ✅

**File**: `app/graphql/pos/validations/exceptions.py`

Exceptions:
- `ValidationError(Exception)` - Base exception
- `PrefixPatternNotFoundError(ValidationError)` - Pattern not found
- `PrefixPatternDuplicateError(ValidationError)` - Duplicate name in org
- `UserNotAuthenticatedError(ValidationError)` - User not authenticated

**File**: `app/graphql/pos/validations/services/prefix_pattern_service.py`

Class: `PrefixPatternService`

Constructor:
- `repository: PrefixPatternRepository`
- `user_org_repository: UserOrgRepository`
- `auth_info: AuthInfo`

Methods:
- `async def _get_user_org_id(self) -> uuid.UUID` - Get org ID from auth_info
- `async def create_pattern(self, name: str, description: str | None = None) -> PrefixPattern`
- `async def get_all_patterns(self) -> list[PrefixPattern]`
- `async def delete_pattern(self, pattern_id: uuid.UUID) -> bool`

Also create:
- `app/graphql/pos/validations/services/__init__.py` - export `PrefixPatternService`

### 2.5 REFACTOR: Clean up and verify ✅

Run `task all`, ensure all tests pass.

---

## Phase 3: GraphQL Layer

Implement GraphQL types, queries, and mutations.

### 3.1 GREEN: Create GraphQL types and inputs ✅

**File**: `app/graphql/pos/validations/strawberry/prefix_pattern_types.py`

Types:
- `PrefixPatternResponse` - GraphQL response DTO
  - `id: strawberry.ID`
  - `name: str`
  - `description: str | None`
  - `created_at: datetime.datetime | None`
  - Static method: `from_model(pattern: PrefixPattern) -> PrefixPatternResponse`

**File**: `app/graphql/pos/validations/strawberry/prefix_pattern_inputs.py`

Inputs:
- `CreatePrefixPatternInput`
  - `name: str`
  - `description: str | None = None`

Also create:
- `app/graphql/pos/validations/strawberry/__init__.py`

### 3.2 RED: Write failing tests for queries ✅

**File**: `tests/graphql/pos/validations/queries/test_prefix_pattern_queries.py`

**Test scenarios**:
- `test_prefix_patterns_returns_list` - Returns list of patterns for user's org
- `test_prefix_patterns_returns_empty_list` - Returns empty list when no patterns

Also create:
- `tests/graphql/pos/validations/queries/__init__.py`

### 3.3 GREEN: Implement queries ✅

**File**: `app/graphql/pos/validations/queries/prefix_pattern_queries.py`

Class: `PrefixPatternQueries`

Methods:
- `async def prefix_patterns(self, service: Injected[PrefixPatternService]) -> list[PrefixPatternResponse]`

Also create:
- `app/graphql/pos/validations/queries/__init__.py` - export `PrefixPatternQueries`

### 3.4 RED: Write failing tests for mutations ✅

**File**: `tests/graphql/pos/validations/mutations/test_prefix_pattern_mutations.py`

**Test scenarios**:
- `test_create_prefix_pattern_success` - Creates pattern and returns response
- `test_create_prefix_pattern_with_description` - Creates pattern with optional description
- `test_create_prefix_pattern_duplicate_returns_error` - Returns error for duplicate name
- `test_delete_prefix_pattern_success` - Deletes pattern and returns True
- `test_delete_prefix_pattern_not_found_returns_error` - Returns error when not found

Also create:
- `tests/graphql/pos/validations/mutations/__init__.py`

### 3.5 GREEN: Implement mutations ✅

**File**: `app/graphql/pos/validations/mutations/prefix_pattern_mutations.py`

Class: `PrefixPatternMutations`

Methods:
- `async def create_prefix_pattern(self, input_data: CreatePrefixPatternInput, service: Injected[PrefixPatternService]) -> PrefixPatternResponse`
- `async def delete_prefix_pattern(self, id: strawberry.ID, service: Injected[PrefixPatternService]) -> bool`

Also create:
- `app/graphql/pos/validations/mutations/__init__.py` - export `PrefixPatternMutations`

### 3.6 GREEN: Wire GraphQL schema ✅

Update `app/graphql/schemas/schema.py`:
- Import `PrefixPatternQueries` and `PrefixPatternMutations`
- Add to Query and Mutation types

### 3.7 GREEN: Register dependency injection ✅

Update `app/core/di/providers.py`:
- Add providers for `PrefixPatternRepository` and `PrefixPatternService`

### 3.8 VERIFY: Run `task all` ✅

---

## Phase 4: Organization Preference

Register the new "Manufacturer Part Number Prefix Removal" preference.

### 4.1 GREEN: Add preference enum and config ✅

**File**: `app/graphql/pos/preferences/enums.py`

Add to `PosPreferenceKey` enum:
- `MANUFACTURER_PART_NUMBER_PREFIX_REMOVAL = "manufacturer_part_number_prefix_removal"`

**File**: `app/graphql/pos/preferences/config.py`

Add to `POS_PREFERENCE_CONFIG`:
- Key: `PosPreferenceKey.MANUFACTURER_PART_NUMBER_PREFIX_REMOVAL.value`
- Value: `PreferenceKeyConfig(allowed_values=["true", "false"])`

### 4.2 VERIFY: Run `task all` ✅

---

## Phase 5: Verification

Manual testing in GraphQL playground.

### 5.1 Test Prefix Patterns ✅

Test the following operations:
- Query `prefixPatterns` returns empty list initially
- Mutation `createPrefixPattern` with name only
- Mutation `createPrefixPattern` with name and description
- Mutation `createPrefixPattern` with duplicate name returns error
- Query `prefixPatterns` returns created patterns
- Mutation `deletePrefixPattern` removes pattern
- Query `prefixPatterns` reflects deletion

### 5.2 Test Organization Preference ✅

Test the following operations:
- Query `organizationPreference` for `manufacturer_part_number_prefix_removal` returns null initially
- Mutation `updateOrganizationPreference` sets to "true"
- Mutation `updateOrganizationPreference` sets to "false"
- Mutation `updateOrganizationPreference` with invalid value returns error

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 2h 19m |
| Phases | 5 |
| Files Modified | 29 |
| Tests Added | 21 |
