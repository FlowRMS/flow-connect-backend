# New User Preferences for POS Domain

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1172](https://linear.app/flow-labs/issue/FLO-1172/flowpos-set-a-routing-method)
- **PR**: [#13](https://github.com/FlowRMS/flow-py-connect/pull/13)
- **Created**: 2026-01-21 15:15 -0300
- **Approved**: 2026-01-21 19:02 -0300
- **Finished**: 2026-01-21 21:28 -0300
- **Commit Prefix**: POS User Preferences

---

## Table of Contents

- [Overview](#overview)
- [Design Pattern](#design-pattern)
- [Critical Files](#critical-files)
- [Phase 1: Registry Infrastructure](#phase-1-registry-infrastructure)
- [Phase 2: POS Preferences Package](#phase-2-pos-preferences-package)
- [Phase 3: Refactor Existing SendMethod](#phase-3-refactor-existing-sendmethod)
- [Phase 4: Verification](#phase-4-verification)
- [Results](#results)

---

## Overview

Add two new user preferences for the POS domain:

| Preference | Type | Description |
|------------|------|-------------|
| **Routing Method** | Enum | Two options: `by_column`, `by_file` |
| **Manufacturer Column** | Text | Free text field (no validation) |

### Architectural Change

**Fully decentralized approach** - each application package owns its preference configuration. To add a new preference for POS, you only modify `pos/preferences/` - **no changes to `user_preferences` required**.

This follows:
- **Open/Closed Principle** - `user_preferences` is open for extension (via registry) but closed for modification
- **Single Responsibility Principle** - `user_preferences` provides generic infrastructure, `pos` owns POS-specific preferences

**GraphQL uses `String` for preference keys** instead of an enum, enabling true extensibility without central modifications.

---

## Design Pattern

**Registry Pattern** - *Martin Fowler, Patterns of Enterprise Application Architecture (2003), Chapter 18*

> "A well-known object that other objects can use to find common objects and services."

**Application**: The `PreferenceConfigRegistry` is the well-known object that `UserPreferenceService` uses to look up validation configs. Each application package (POS, CRM, etc.) registers its own config into the registry.

**Reference**: https://martinfowler.com/eaaCatalog/registry.html

---

## Critical Files

| File | Action | Description |
|------|--------|-------------|
| [`app/graphql/settings/user_preferences/models/registry.py`](../../app/graphql/settings/user_preferences/models/registry.py) | ✅ Create | PreferenceConfigRegistry |
| [`app/graphql/settings/user_preferences/models/types.py`](../../app/graphql/settings/user_preferences/models/types.py) | ✅ Create | PreferenceKeyConfig dataclass |
| [`app/graphql/settings/user_preferences/services/user_preference_service.py`](../../app/graphql/settings/user_preferences/services/user_preference_service.py) | ✅ Modify | Use registry for validation |
| [`app/graphql/pos/preferences/enums.py`](../../app/graphql/pos/preferences/enums.py) | ✅ Create | POS preference keys and value enums |
| [`app/graphql/pos/preferences/config.py`](../../app/graphql/pos/preferences/config.py) | ✅ Create | POS preference config |
| [`app/graphql/pos/preferences/registration.py`](../../app/graphql/pos/preferences/registration.py) | ✅ Create | Register POS config into registry |
| `app/graphql/settings/user_preferences/models/enums.py` | ✅ Delete | No longer needed (full decentralization) |
| `app/graphql/settings/user_preferences/config.py` | ✅ Remove | Deleted (replaced by registry) |
| [`app/graphql/settings/user_preferences/strawberry/user_preference_types.py`](../../app/graphql/settings/user_preferences/strawberry/user_preference_types.py) | ✅ Modify | Import enums from pos package |

---

## Phase 1: Registry Infrastructure

*Create the registry and update the service to use it.*

### 1.1 RED: Write failing tests for registry ✅

**File**: [`tests/graphql/settings/user_preferences/test_registry.py`](../../tests/graphql/settings/user_preferences/test_registry.py)

**Test scenarios**:
- `test_register_and_get_config` - Register a config and retrieve it by application
- `test_get_config_returns_none_for_unknown_app` - Returns None for unregistered application
- `test_get_allowed_values_from_registry` - Retrieves allowed values for a specific key

### 1.2 GREEN: Implement registry ✅

**File**: [`app/graphql/settings/user_preferences/models/registry.py`](../../app/graphql/settings/user_preferences/models/registry.py)

- `PreferenceConfigRegistry` class with:
  - `register(application: str, config: dict[str, PreferenceKeyConfig])` - Register config for an application
  - `get_config(application: str)` - Get config for an application
  - `get_allowed_values(application: str, key: str)` - Get allowed values for a key
- Module-level instance: `preference_registry = PreferenceConfigRegistry()`

**Additional file**: [`app/graphql/settings/user_preferences/models/types.py`](../../app/graphql/settings/user_preferences/models/types.py) - `PreferenceKeyConfig` dataclass (in models/ to avoid circular imports)

### 1.3 GREEN: Update service to use registry ✅

**File**: [`app/graphql/settings/user_preferences/services/user_preference_service.py`](../../app/graphql/settings/user_preferences/services/user_preference_service.py)

- Import `preference_registry`
- Replace `get_allowed_values()` call from `config.py` with `preference_registry.get_allowed_values()`

### 1.4 VERIFY: Run checks ✅

Run `task all` - all checks pass.

---

## Phase 2: POS Preferences Package

*Create the POS preferences package with new preferences.*

### 2.1 RED: Write failing tests for POS preferences ✅

**File**: [`tests/graphql/pos/preferences/test_pos_preferences.py`](../../tests/graphql/pos/preferences/test_pos_preferences.py)

**Test scenarios**:
- `test_set_routing_method_valid_values` - Setting `by_column` and `by_file` should succeed
- `test_set_routing_method_invalid_value` - Setting invalid value should raise `InvalidPreferenceValueError`
- `test_set_manufacturer_column` - Setting any text value should succeed (no validation)

### 2.2 GREEN: Create POS preferences package ✅

**File**: [`app/graphql/pos/preferences/enums.py`](../../app/graphql/pos/preferences/enums.py)
- `PosPreferenceKey(StrEnum)`: `SEND_METHOD`, `ROUTING_METHOD`, `MANUFACTURER_COLUMN`
- `SendMethod(StrEnum)`: `UPLOAD_FILE`, `API`, `SFTP`, `EMAIL`
- `RoutingMethod(StrEnum)`: `BY_COLUMN`, `BY_FILE`

**File**: [`app/graphql/pos/preferences/config.py`](../../app/graphql/pos/preferences/config.py)
- `POS_PREFERENCE_CONFIG` dict mapping `PosPreferenceKey` → `PreferenceKeyConfig`
- Only `SEND_METHOD` and `ROUTING_METHOD` have `allowed_values`
- `MANUFACTURER_COLUMN` has no validation (free text)

**File**: [`app/graphql/pos/preferences/registration.py`](../../app/graphql/pos/preferences/registration.py)
- Import `preference_registry` from `user_preferences`
- Call `preference_registry.register(Application.POS, POS_PREFERENCE_CONFIG)`

**Service update**: Updated `user_preference_service.py` to accept `StrEnum` for key parameter (enables app-specific preference keys)

### 2.3 VERIFY: Run checks ✅

Run `task all` - all 20 tests pass.

---

## Phase 3: Refactor Existing SendMethod

*Move POS-specific code out of user_preferences.*

### 3.1 REFACTOR: Clean up user_preferences ✅

**Full decentralization** - Changed GraphQL to use `String` instead of `PreferenceKey` enum, so adding new preferences requires NO changes to `user_preferences`.

**File**: `app/graphql/settings/user_preferences/models/enums.py`
- Deleted entirely (no longer needed)

**File**: `app/graphql/settings/user_preferences/config.py`
- Deleted (replaced by registry + pos/preferences registration)

**File**: [`app/graphql/settings/user_preferences/strawberry/user_preference_types.py`](../../app/graphql/settings/user_preferences/strawberry/user_preference_types.py)
- Changed `key: PreferenceKey` to `key: str`
- Removed `PreferenceKey` import and Strawberry registration

**File**: [`app/graphql/settings/user_preferences/queries/user_preference_queries.py`](../../app/graphql/settings/user_preferences/queries/user_preference_queries.py)
- Changed `key: PreferenceKey` parameter to `key: str`

**File**: [`app/graphql/settings/user_preferences/mutations/user_preference_mutations.py`](../../app/graphql/settings/user_preferences/mutations/user_preference_mutations.py)
- Changed `key: PreferenceKey` parameter to `key: str`

**File**: [`app/graphql/settings/user_preferences/services/user_preference_service.py`](../../app/graphql/settings/user_preferences/services/user_preference_service.py)
- Changed key parameter type from `StrEnum` to `StrEnum | str`
- Added `_get_key_value()` helper to handle both types

**File**: [`tests/graphql/settings/user_preferences/services/test_user_preference_service.py`](../../tests/graphql/settings/user_preferences/services/test_user_preference_service.py)
- Updated to use `PosPreferenceKey` from `pos/preferences/enums.py`

### 3.2 VERIFY: Run checks ✅

Run `task all` - all 20 tests pass, GraphQL schema updated with `key: String!`.

---

## Phase 4: Verification ✅

*Manual testing via GraphQL Playground.*

### 4.1 Test new preferences ✅

1. ✅ Set routing method to `by_column` - succeeded
2. ✅ Set routing method to invalid value - rejected with proper error message
3. ✅ Set manufacturer column to "Brand" - succeeded (free text)
4. ✅ Query preferences by application - returned all 3 POS preferences

### 4.2 Test existing send_method still works ✅

1. ✅ Set send method to `api` - succeeded

---

## Results

| Metric | Value |
|--------|-------|
| Phases | 4 |
| Files Created | 8 |
| Files Modified | 6 |
| Files Deleted | 2 |
| Tests Added | 10 |
| Total Lines | +495 / -80 |
