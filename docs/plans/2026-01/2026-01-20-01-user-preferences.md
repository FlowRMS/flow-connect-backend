# User Preferences

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1139](https://linear.app/flow-labs/issue/FLO-1139/flowpos-user-preferences)
- **Created**: 2026-01-20 15:58 -03
- **Approved**: 2026-01-20 16:46 -03
- **Finished**: 2026-01-20 21:28 -03
- **PR**: [#10](https://github.com/FlowRMS/flow-py-connect/pull/10)
- **Commit Prefix**: User Preferences

---

## Table of Contents

- [Overview](#overview)
- [Critical Files](#critical-files)
- [Phase 1: Database Schema](#phase-1-database-schema)
- [Phase 2: Repository & Service](#phase-2-repository--service)
- [Phase 3: GraphQL Layer](#phase-3-graphql-layer)
- [Phase 4: Verification](#phase-4-verification)
- [Results](#results)

---

## Overview

Implement a user preferences system that allows users to store and retrieve their preferences. The initial preference is **Send Method** with 4 possible values:
- `upload_file`
- `api`
- `sftp`
- `email`

The system is designed for extensibility - new preferences can be added in the future with different options or free text values.

### Design Decisions

1. **Key-Value Model**: Simple `application` + `preference_key` + `preference_value` structure for flexibility
2. **Unique Constraint**: One value per user per application per preference key `(user_id, application, preference_key)`
3. **Schema**: `connect_pos` (user-specific POS-related data)
4. **Validation**: Service layer validates allowed values per preference key
5. **Application Column**: String in DB with code enum (`Application`) for validation - easy to migrate to reference table later
6. **Package Structure**: `settings/user_preferences/` - settings is the parent domain, user_preferences is a sub-module (future: org_preferences, etc.)

---

## Critical Files

| File | Status | Description |
|------|--------|-------------|
| [`app/graphql/settings/applications/models/enums.py`](../../app/graphql/settings/applications/models/enums.py) | ✅ | Application enum |
| [`app/graphql/settings/user_preferences/models/user_preference.py`](../../app/graphql/settings/user_preferences/models/user_preference.py) | ✅ | SQLAlchemy model |
| [`app/graphql/settings/user_preferences/models/enums.py`](../../app/graphql/settings/user_preferences/models/enums.py) | ✅ | Enums (PreferenceKey, SendMethod) |
| [`app/graphql/settings/user_preferences/config.py`](../../app/graphql/settings/user_preferences/config.py) | ✅ | Preference config (validation rules) |
| [`alembic/versions/20260120_create_user_preferences.py`](../../alembic/versions/20260120_create_user_preferences.py) | ✅ | Database migration |
| [`app/graphql/settings/user_preferences/repositories/user_preference_repository.py`](../../app/graphql/settings/user_preferences/repositories/user_preference_repository.py) | ✅ | Repository |
| [`app/graphql/settings/user_preferences/services/user_preference_service.py`](../../app/graphql/settings/user_preferences/services/user_preference_service.py) | ✅ | Service |
| [`app/graphql/settings/user_preferences/exceptions.py`](../../app/graphql/settings/user_preferences/exceptions.py) | ✅ | Exceptions |
| [`tests/graphql/settings/user_preferences/services/test_user_preference_service.py`](../../tests/graphql/settings/user_preferences/services/test_user_preference_service.py) | ✅ | Service tests |
| [`app/graphql/settings/user_preferences/strawberry/user_preference_types.py`](../../app/graphql/settings/user_preferences/strawberry/user_preference_types.py) | ✅ | GraphQL response types |
| [`app/graphql/settings/user_preferences/queries/user_preference_queries.py`](../../app/graphql/settings/user_preferences/queries/user_preference_queries.py) | ✅ | GraphQL queries |
| [`app/graphql/settings/user_preferences/mutations/user_preference_mutations.py`](../../app/graphql/settings/user_preferences/mutations/user_preference_mutations.py) | ✅ | GraphQL mutations |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | ✅ | Schema registration |

---

## Phase 1: Database Schema

*Create the model, enums, and migration for user preferences.*

### 1.1 GREEN: Create enums ✅

**File**: [`app/graphql/settings/user_preferences/models/enums.py`](../../app/graphql/settings/user_preferences/models/enums.py)

Define three enums:

1. **Application** (StrEnum): Defines allowed applications
   - `POS = "pos"`

2. **PreferenceKey** (StrEnum): Defines allowed preference keys
   - `SEND_METHOD = "send_method"`

3. **SendMethod** (StrEnum): Defines allowed values for the send_method preference
   - `UPLOAD_FILE = "upload_file"`
   - `API = "api"`
   - `SFTP = "sftp"`
   - `EMAIL = "email"`

### 1.2 GREEN: Create model ✅

**File**: [`app/graphql/settings/user_preferences/models/user_preference.py`](../../app/graphql/settings/user_preferences/models/user_preference.py)

**Inheritance**: `PyConnectPosBaseModel`, `HasCreatedAt`

**Table**: `user_preferences` (schema: `connect_pos`)

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK, default uuid4 (from base) |
| `user_id` | UUID | NOT NULL |
| `application` | String(50) | NOT NULL |
| `preference_key` | String(50) | NOT NULL |
| `preference_value` | Text | NULL (set to null to reset) |
| `created_at` | TIMESTAMP(tz) | NOT NULL, default now() (from HasCreatedAt) |
| `updated_at` | TIMESTAMP(tz) | NOT NULL, default now(), onupdate now() (manual) |

**Note**: No `HasUpdatedAt` mixin exists in commons. Adding `updated_at` manually since preferences are upserted and knowing when they were last changed is useful.

**Constraints**:
- Unique constraint on `(user_id, application, preference_key)`

### 1.3 GREEN: Create migration ✅

**File**: [`alembic/versions/20260120_create_user_preferences.py`](../../alembic/versions/20260120_create_user_preferences.py)

- Create `user_preferences` table in `connect_pos` schema
- Add unique constraint on `(user_id, application, preference_key)`
- Include proper `upgrade()` and `downgrade()` functions

### 1.4 VERIFY: Run checks ✅

Run `task all` to verify type checks and linting pass.

---

## Phase 2: Repository & Service

*Implement the data access and business logic layers with TDD.*

### 2.1 RED: Write failing tests for service ✅

**File**: [`tests/graphql/settings/user_preferences/services/test_user_preference_service.py`](../../tests/graphql/settings/user_preferences/services/test_user_preference_service.py)

**Test scenarios**:
- `test_get_preference_returns_value_when_exists` - Returns preference value when it exists for given application/key
- `test_get_preference_returns_none_when_not_exists` - Returns None when preference doesn't exist
- `test_get_preference_returns_none_when_value_is_null` - Returns None when preference exists but value is null
- `test_get_preferences_by_application_returns_list` - Returns list of preferences for an application
- `test_get_all_preferences_returns_dict` - Returns dict of all user preferences grouped by application
- `test_set_preference_creates_new_when_not_exists` - Creates new preference when it doesn't exist
- `test_set_preference_updates_when_exists` - Updates existing preference (same application/key)
- `test_set_preference_with_null_resets_value` - Setting value to null resets the preference
- `test_set_preference_validates_application` - Raises error for invalid application
- `test_set_preference_validates_send_method_value` - Raises error for invalid send_method value in pos application

### 2.2 GREEN: Implement repository ✅

**File**: [`app/graphql/settings/user_preferences/repositories/user_preference_repository.py`](../../app/graphql/settings/user_preferences/repositories/user_preference_repository.py)

**Methods**:
- `get_by_user_application_key(user_id, application, key)` → `UserPreference | None`
- `get_by_user_and_application(user_id, application)` → `list[UserPreference]`
- `get_all_by_user(user_id)` → `list[UserPreference]`
- `upsert(user_id, application, key, value)` → `UserPreference` (value can be null to reset)

### 2.3 GREEN: Implement service ✅

**File**: [`app/graphql/settings/user_preferences/services/user_preference_service.py`](../../app/graphql/settings/user_preferences/services/user_preference_service.py)

**Methods**:
- `get_preference(application, key)` → `str | None`
- `get_preferences_by_application(application)` → `list[UserPreference]`
- `get_all_preferences()` → `dict[str, list[UserPreference]]` (grouped by application)
- `set_preference(application, key, value)` → `UserPreference` (value can be null to reset)

**Validation**:
- Application must be in `Application` enum
- For `pos` application + `send_method` key: value must be in `SendMethod` enum (or null)
- Other keys: accept any string value or null (future extensibility)

### 2.4 REFACTOR: Restructure to settings/user_preferences ✅

Structural changes (no behavior change, all tests still pass):

**Package restructure:**
- `app/graphql/user_preferences/` → `app/graphql/settings/user_preferences/`
- `tests/graphql/user_preferences/` → `tests/graphql/settings/user_preferences/`

**Naming changes:**
- Enum: `PreferencePackage` → `Application`
- DB column: `package` → `application`
- Constraint: `uq_user_preferences_user_package_key` → `uq_user_preferences_user_application_key`
- Exception: `InvalidPackageError` → `InvalidApplicationError`
- Repository methods: `get_by_user_package_key` → `get_by_user_application_key`, `get_by_user_and_package` → `get_by_user_and_application`
- Service methods: `get_preferences_by_package` → `get_preferences_by_application`

**Rationale:** "settings" is the parent domain for future extensibility (org_preferences, etc.). "application" better describes what POS, CRM, etc. represent.

### 2.5 REFACTOR: Extract Application enum to applications package ✅

Created `settings/applications/` as a sibling package to `user_preferences/`:

```
app/graphql/settings/
├── applications/           # New package
│   └── models/
│       └── enums.py        # Application enum
└── user_preferences/
    └── models/
        └── enums.py        # PreferenceKey, SendMethod only
```

**Rationale:** `Application` is a broader concept used by multiple settings modules. Future modules (org_preferences, etc.) will also reference it.

### 2.6 REFACTOR: Config-driven preference validation ✅

**File**: [`app/graphql/settings/user_preferences/config.py`](../../app/graphql/settings/user_preferences/config.py)

Replaced hardcoded validation logic with a declarative configuration:

```python
PREFERENCE_CONFIG: dict[Application, dict[PreferenceKey, PreferenceKeyConfig]] = {
    Application.POS: {
        PreferenceKey.SEND_METHOD: PreferenceKeyConfig(
            allowed_values=[m.value for m in SendMethod],
        ),
    },
}
```

**Benefits:**
- Easy to add new preference keys per application
- Validation logic is centralized in `get_allowed_values()` helper
- Service uses config instead of hardcoded if/else

### 2.7 VERIFY: Run checks ✅

Run `task all` to verify all tests pass.

---

## Phase 3: GraphQL Layer

*Add GraphQL types, queries, and mutations.*

### 3.1 GREEN: Create Strawberry types ✅

**File**: [`app/graphql/settings/user_preferences/strawberry/user_preference_types.py`](../../app/graphql/settings/user_preferences/strawberry/user_preference_types.py)

- Register `Application`, `PreferenceKey`, and `SendMethod` enums with Strawberry
- Create `UserPreferenceResponse` type with `application`, `key`, `value` fields

### 3.2 GREEN: Create queries ✅

**File**: [`app/graphql/settings/user_preferences/queries/user_preference_queries.py`](../../app/graphql/settings/user_preferences/queries/user_preference_queries.py)

**Queries** (Python snake_case → GraphQL camelCase):
- `user_preference` → `userPreference(application, key)` → `UserPreferenceResponse | None`
- `user_preferences_by_application` → `userPreferencesByApplication(application)` → `list[UserPreferenceResponse]`
- `user_preferences` → `userPreferences` → `list[UserPreferenceResponse]` (all preferences)

### 3.3 GREEN: Create mutations ✅

**File**: [`app/graphql/settings/user_preferences/mutations/user_preference_mutations.py`](../../app/graphql/settings/user_preferences/mutations/user_preference_mutations.py)

**Mutations** (Python snake_case → GraphQL camelCase):
- `update_user_preference` → `updateUserPreference(application, key, value)` → `UserPreferenceResponse` (pass null value to reset)

### 3.4 GREEN: Register in schema ✅

**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

- Add `UserPreferenceQueries` to `Query` class
- Add `UserPreferenceMutations` to `Mutation` class

### 3.5 VERIFY: Run checks ✅

Run `task all` to verify all checks pass.

---

## Phase 4: Verification

*Manual testing in GraphQL playground.*

### 4.1 Test GraphQL operations ✅

Test in GraphQL playground (http://localhost:8010/graphql):

1. **Set preference** - `updateUserPreference` with application: POS, key: SEND_METHOD, value: "api"
2. **Get single preference** - `userPreference` with application: POS, key: SEND_METHOD
3. **Get preferences by application** - `userPreferencesByApplication` with application: POS
4. **Get all preferences** - `userPreferences`
5. **Reset preference** - `updateUserPreference` with value: null
6. **Test validation** - `updateUserPreference` with invalid value (should fail)

---

## Changes During Testing

- **Renamed mutation**: `setUserPreference(input)` → `updateUserPreference(application, key, value)` to align with flow-py-backend patterns (e.g., `updateCompany(id, input)`)
- **Removed**: `SetPreferenceInput` input type (no longer needed with direct parameters)
- **Files modified**: `user_preference_mutations.py`
- **Files deleted**: `user_preference_inputs.py`

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~5h |
| Phases | 4 |
| Files Modified | 30 |
| Tests Added | 10 |
