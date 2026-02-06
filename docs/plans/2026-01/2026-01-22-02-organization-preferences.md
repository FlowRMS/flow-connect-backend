# User Preferences to Organization Preferences

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1197](https://linear.app/flow-labs/issue/FLO-1197/flowpos-user-preferences-to-organization-preferences)
- **Created**: 2026-01-22 11:49 -03
- **Approved**: 2026-01-22 11:56 -03
- **Finished**: 2026-01-22 12:59 -03
- **PR**: [#15](https://github.com/FlowRMS/flow-py-connect/pull/15)
- **Commit Prefix**: Organization Preferences

---

## Table of Contents

- [Overview](#overview)
- [Critical Files](#critical-files)
- [Phase 1: Database Model](#phase-1-database-model)
- [Phase 2: Repository Layer](#phase-2-repository-layer)
- [Phase 3: Service Layer](#phase-3-service-layer)
- [Phase 4: GraphQL Layer](#phase-4-graphql-layer)
- [Phase 5: Verification](#phase-5-verification)
- [Results](#results)

---

## Overview

Refactor the `user_preferences` package to `organization_preferences`. The preferences currently stored per-user actually belong to organizations - all members of an organization should see the same preferences.

### Key Changes

1. **Model**: `UserPreference` → `OrganizationPreference`, `user_id` → `organization_id`
2. **Database**: Table rename `user_preferences` → `organization_preferences`
3. **Package**: Directory rename `user_preferences/` → `organization_preferences/`
4. **Service**: Use `UserOrgRepository` to get organization_id (pattern from `OrganizationAliasService`)
5. **GraphQL**: Rename all types, queries, and mutations

### Design Pattern Reference

- **Repository Pattern** (Martin Fowler) - Data access layer remains unchanged in structure
- **Dependency Injection** - Service will inject `UserOrgRepository` for org lookup

---

## Critical Files

| File | Action | Status |
|------|--------|--------|
| [`app/graphql/settings/organization_preferences/`](../../app/graphql/settings/organization_preferences/) | Create (rename from user_preferences) | ✅ |
| [`app/graphql/settings/organization_preferences/models/organization_preference.py`](../../app/graphql/settings/organization_preferences/models/organization_preference.py) | Create | ✅ |
| [`app/graphql/settings/organization_preferences/repositories/organization_preference_repository.py`](../../app/graphql/settings/organization_preferences/repositories/organization_preference_repository.py) | Create | ✅ |
| [`app/graphql/settings/organization_preferences/services/organization_preference_service.py`](../../app/graphql/settings/organization_preferences/services/organization_preference_service.py) | Create | ✅ |
| [`app/graphql/settings/organization_preferences/strawberry/organization_preference_types.py`](../../app/graphql/settings/organization_preferences/strawberry/organization_preference_types.py) | Create | ✅ |
| [`app/graphql/settings/organization_preferences/queries/organization_preference_queries.py`](../../app/graphql/settings/organization_preferences/queries/organization_preference_queries.py) | Create | ✅ |
| [`app/graphql/settings/organization_preferences/mutations/organization_preference_mutations.py`](../../app/graphql/settings/organization_preferences/mutations/organization_preference_mutations.py) | Create | ✅ |
| [`alembic/versions/20260122_rename_to_organization_preferences.py`](../../alembic/versions/20260122_rename_to_organization_preferences.py) | Create | ✅ |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | Modify | ✅ |
| [`tests/graphql/settings/organization_preferences/`](../../tests/graphql/settings/organization_preferences/) | Create | ✅ |

---

## Phase 1: Database Model

Rename model and table, change `user_id` to `organization_id`.

### 1.1 GREEN: Create migration for table rename ✅

**File**: [`alembic/versions/20260122_rename_to_organization_preferences.py`](../../alembic/versions/20260122_rename_to_organization_preferences.py)

Migration operations:
- Rename table: `user_preferences` → `organization_preferences`
- Rename column: `user_id` → `organization_id`
- Rename constraint: `uq_user_preferences_user_application_key` → `uq_org_preferences_org_application_key`

### 1.2 GREEN: Create OrganizationPreference model ✅

**File**: [`app/graphql/settings/organization_preferences/models/organization_preference.py`](../../app/graphql/settings/organization_preferences/models/organization_preference.py)

Changes from `UserPreference`:
- Class name: `OrganizationPreference`
- Table name: `organization_preferences`
- Column: `organization_id: Mapped[uuid.UUID]` (replaces `user_id`)
- Constraint name: `uq_org_preferences_org_application_key`

### 1.3 GREEN: Move supporting models ✅

**Files**:
- [`models/types.py`](../../app/graphql/settings/organization_preferences/models/types.py) (PreferenceKeyConfig)
- [`models/registry.py`](../../app/graphql/settings/organization_preferences/models/registry.py) (PreferenceConfigRegistry, preference_registry)
- [`exceptions.py`](../../app/graphql/settings/organization_preferences/exceptions.py) (renamed exception classes)

### 1.4 VERIFY: Run `task all` ✅

---

## Phase 2: Repository Layer

Create repository with organization-focused methods.

### 2.1 RED: Write failing tests for repository ✅

**File**: [`tests/graphql/settings/organization_preferences/repositories/test_organization_preference_repository.py`](../../tests/graphql/settings/organization_preferences/repositories/test_organization_preference_repository.py)

**Test scenarios**:
- `test_returns_preference_when_found` - Finds existing preference
- `test_returns_none_when_not_found` - Returns None when not found
- `test_returns_list_of_preferences` - Returns all preferences for org+app
- `test_returns_all_preferences_for_org` - Returns all preferences for organization
- `test_creates_new_preference` - Creates when doesn't exist
- `test_updates_existing_preference` - Updates when exists

### 2.2 GREEN: Implement OrganizationPreferenceRepository ✅

**File**: [`app/graphql/settings/organization_preferences/repositories/organization_preference_repository.py`](../../app/graphql/settings/organization_preferences/repositories/organization_preference_repository.py)

Methods (signature changes only):
- `get_by_org_application_key(organization_id, application, key)` → `OrganizationPreference | None`
- `get_by_org_and_application(organization_id, application)` → `list[OrganizationPreference]`
- `get_all_by_org(organization_id)` → `list[OrganizationPreference]`
- `upsert(organization_id, application, key, value)` → `OrganizationPreference`

### 2.3 VERIFY: Run `task all` ✅

---

## Phase 3: Service Layer

Update service to resolve organization_id from auth context.

### 3.1 RED: Write failing tests for service ✅

**File**: [`tests/graphql/settings/organization_preferences/services/test_organization_preference_service.py`](../../tests/graphql/settings/organization_preferences/services/test_organization_preference_service.py)

**Test scenarios**:
- `test_returns_value_when_preference_exists` - Returns preference value
- `test_returns_none_when_preference_not_found` - Returns None
- `test_returns_none_for_null_value` - Handles null value
- `test_returns_list_for_application` - Returns list for application
- `test_groups_by_application` - Groups results correctly
- `test_creates_new_preference` - Creates new preference
- `test_updates_existing_preference` - Updates existing
- `test_resets_with_none_value` - Resets to null
- `test_invalid_application_raises_error` - Validates application
- `test_invalid_preference_value_raises_error` - Validates against registry

### 3.2 GREEN: Implement OrganizationPreferenceService ✅

**File**: [`app/graphql/settings/organization_preferences/services/organization_preference_service.py`](../../app/graphql/settings/organization_preferences/services/organization_preference_service.py)

Key changes from `UserPreferenceService`:
- Inject `UserOrgRepository` (pattern from `OrganizationAliasService`)
- Add `_get_organization_id()` method using `user_org_repository.get_user_org_id()`
- Replace all `auth_info.flow_user_id` with `await self._get_organization_id()`
- Update method parameter names: `user_id` → `organization_id`

**Also updated** (dependency for service validation):
- [`app/graphql/pos/preferences/config.py`](../../app/graphql/pos/preferences/config.py) - Import from organization_preferences
- [`app/graphql/pos/preferences/registration.py`](../../app/graphql/pos/preferences/registration.py) - Use new preference_registry

### 3.3 VERIFY: Run `task all` ✅

---

## Phase 4: GraphQL Layer

Rename types, queries, and mutations.

### 4.1 GREEN: Create GraphQL types ✅

**File**: [`app/graphql/settings/organization_preferences/strawberry/organization_preference_types.py`](../../app/graphql/settings/organization_preferences/strawberry/organization_preference_types.py)

- Renamed `UserPreferenceResponse` → `OrganizationPreferenceResponse`
- Updated `from_model()` to use `OrganizationPreference`

### 4.2 GREEN: Create queries ✅

**File**: [`app/graphql/settings/organization_preferences/queries/organization_preference_queries.py`](../../app/graphql/settings/organization_preferences/queries/organization_preference_queries.py)

Renamed class and methods:
- `UserPreferenceQueries` → `OrganizationPreferenceQueries`
- `user_preference` → `organization_preference`
- `user_preferences_by_application` → `organization_preferences_by_application`
- `user_preferences` → `organization_preferences`

### 4.3 GREEN: Create mutations ✅

**File**: [`app/graphql/settings/organization_preferences/mutations/organization_preference_mutations.py`](../../app/graphql/settings/organization_preferences/mutations/organization_preference_mutations.py)

Renamed class and methods:
- `UserPreferenceMutations` → `OrganizationPreferenceMutations`
- `update_user_preference` → `update_organization_preference`

### 4.4 GREEN: Update schema registration ✅

**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

- Updated imports to use `organization_preferences` package
- Updated class names in Query and Mutation classes

### 4.5 GREEN: Update POS preferences integration ✅

_(Done in Phase 3 as service dependency)_

**File**: [`app/graphql/pos/preferences/registration.py`](../../app/graphql/pos/preferences/registration.py)

- Updated import from `organization_preferences` package (preference_registry)

**File**: [`app/graphql/pos/preferences/config.py`](../../app/graphql/pos/preferences/config.py)

- Updated import for `PreferenceKeyConfig`

### 4.6 VERIFY: Run `task all` ✅

---

## Phase 5: Verification

Final cleanup and manual testing.

### 5.1 Delete old user_preferences package ✅

Removed entire directories:
- `app/graphql/settings/user_preferences/`
- `tests/graphql/settings/user_preferences/`

### 5.2 Update POS preferences test ✅

**File**: [`tests/graphql/pos/preferences/test_pos_preferences.py`](../../tests/graphql/pos/preferences/test_pos_preferences.py)

- Updated imports to use `organization_preferences`
- Updated service to use `OrganizationPreferenceService` with `UserOrgRepository`
- Updated mock to use `organization_id` instead of `flow_user_id`

### 5.3 VERIFY: Run `task all` ✅

### 5.4 Manual Testing ✅

Tested in GraphQL playground:
- ✅ Query `organizationPreference` with valid application and key
- ✅ Query `organizationPreferences` to get all preferences
- ✅ Mutation `updateOrganizationPreference` to set a value
- ✅ Validation rejects invalid values with clear error message

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 1h 10m |
| Phases | 5 |
| Files Modified | 34 |
| Tests Added | 16 |
