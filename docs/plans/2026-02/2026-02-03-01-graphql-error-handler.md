# Implement GraphQL Error Handler to Show Custom Exception Messages

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1483](https://linear.app/flow-labs/issue/FLO-1483/fix-graphql-error-handling-to-display-remoteapierror-messages)
- **Created**: 2026-02-03 00:12 -03
- **Approved**: 2026-02-03 08:46 -03
- **Finished**: 2026-02-03 11:40 -03
- **PR**: [#31](https://github.com/FlowRMS/flow-py-connect/pull/31)
- **Commit Prefix**: GraphQL Error Handler

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: Implement MaskErrors with should_mask_error](#phase-1-implement-maskerrors-with-should_mask_error)
- [Phase 2: Migrate Domain Exceptions to BaseException](#phase-2-migrate-domain-exceptions-to-baseexception)
- [Phase 3: Verification](#phase-3-verification)
- [Review](#review)
- [Results](#results)


---

## Overview

**Problem**: Custom exceptions return "Unexpected error." instead of the actual error message in GraphQL responses. This affects both:
- Common exceptions (like `RemoteApiError`) defined in `app/errors/common_errors.py` that extend `BaseException`
- Domain exceptions (like `PrefixPatternNotFoundError`, `NoPendingFilesError`) defined in each domain's `exceptions.py` that extend plain `Exception`

Additionally, the schema has no error masking, meaning internal errors (e.g., `ValueError`, `KeyError`) could leak implementation details to API consumers.

**Example**:
- **Expected**: `"A pending connection request already exists."` with `extensions: {"exception": "RemoteApiError"}`
- **Actual**: `"Unexpected error."` (with MaskErrors) or raw internal error message (without it)

**Root Cause**: Two issues:
1. The schema lacks the `MaskErrors` extension — Strawberry's idiomatic way to control which errors are exposed to clients
2. Domain exceptions extend plain `Exception` instead of `BaseException`, so they are not recognized as user-facing errors

**Solution**:
1. Add `MaskErrors` extension with a custom `should_mask_error` function that allows `BaseException` subclasses through and hides everything else
2. Migrate all domain exceptions to extend `BaseException` so they are consistently treated as user-facing errors

---

## Design Decisions

### DD-1: Use MaskErrors Extension with should_mask_error

**Decision**: Use Strawberry's built-in `MaskErrors` extension with a custom `should_mask_error` function, rather than `process_errors` or `debug=True`.

- `debug=True` would expose ALL error details, including stack traces — security risk
- `process_errors` on Schema is a logging hook only — it does NOT modify the response
- `strawberry.Schema()` does not accept a `process_errors` constructor parameter
- `MaskErrors` is Strawberry's recommended pattern ([MaskErrors extension](https://strawberry.rocks/docs/extensions/mask-errors)) for production error handling
- `should_mask_error` receives a `GraphQLError` and returns `bool` — `False` means "show the real message", `True` means "replace with generic message"
- Our `BaseException` subclasses set `original_error=self` in their constructor, so we can check `isinstance(error.original_error, BaseException)`

### DD-2: Migrate Domain Exceptions to BaseException (Marker Interface Pattern)

**Decision**: All domain-specific exceptions should extend `BaseException` instead of plain `Exception`.

- Creates a single rule: "extends `BaseException` = user-facing error" ([Marker Interface pattern](https://en.wikipedia.org/wiki/Marker_interface_pattern))
- `should_mask_error` stays simple — no need to maintain a list of domain exception classes
- Domain exceptions automatically get the `extensions` field with their class name (useful for frontend error handling)
- Audit confirmed 30 of 32 domain exceptions are directly compatible (raised with `message: str`)
- 2 exceptions in `connections/exceptions.py` have custom constructors — need minor refactoring to call `BaseException.__init__(message)` correctly

---

## Critical Files

| File                                                         | Action | Description                                         |
|--------------------------------------------------------------|--------|-----------------------------------------------------|
| [`app/graphql/error_handler.py`](../../app/graphql/error_handler.py) | Create | `should_mask_error` function                        |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | Modify | Add `MaskErrors` extension with `should_mask_error` |
| [`tests/graphql/test_error_handler.py`](../../tests/graphql/test_error_handler.py) | Create | Unit tests for `should_mask_error`                  |
| `app/graphql/pos/validations/exceptions.py`                  | Modify | Extend `BaseException` instead of `Exception`       |
| `app/graphql/pos/organization_alias/exceptions.py`           | Modify | Extend `BaseException` instead of `Exception`       |
| `app/graphql/connections/exceptions.py`                      | Modify | Extend `BaseException`, refactor constructors       |
| `app/graphql/pos/data_exchange/exceptions.py`                | Modify | Extend `BaseException` instead of `Exception`       |
| `app/graphql/pos/agreement/exceptions.py`                    | Modify | Extend `BaseException` instead of `Exception`       |
| `app/graphql/pos/field_map/exceptions.py`                    | Modify | Extend `BaseException` instead of `Exception`       |
| `app/graphql/settings/organization_preferences/exceptions.py`| Modify | Extend `BaseException` instead of `Exception`       |

---

## Phase 1: Implement MaskErrors with should_mask_error

_Implement the error handler following TDD methodology._

### 1.1 RED: Write failing tests for should_mask_error ✅

**File**: [`tests/graphql/test_error_handler.py`](../../tests/graphql/test_error_handler.py)

**Test scenarios**:
- `test_does_not_mask_base_exception` - Returns `False` for `BaseException` subclasses (message is shown)
- `test_masks_non_base_exception` - Returns `True` for non-custom exceptions (message is hidden)
- `test_does_not_mask_error_without_original_error` - Returns `False` for GraphQL errors without `original_error` (e.g., syntax errors)

### 1.2 GREEN: Implement should_mask_error function ✅

**File**: [`app/graphql/error_handler.py`](../../app/graphql/error_handler.py)

**Implementation**:
- Create `should_mask_error` function that receives a `GraphQLError` and returns `bool`
- If `original_error` is instance of `BaseException`, return `False` (don't mask — show the message)
- If `original_error` is any other exception, return `True` (mask — hide internal details)
- If no `original_error` (pure GraphQL errors like syntax errors), return `False` (show as-is)

### 1.3 GREEN: Integrate into schema ✅

**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

- Import `MaskErrors` from `strawberry.extensions.mask_errors`
- Import `should_mask_error` from `app.graphql.error_handler`
- Add `MaskErrors(should_mask_error=should_mask_error)` to the `extensions` list

### 1.4 VERIFY: Run task all ✅

Run `task all` to confirm all checks pass.

---

## Phase 2: Migrate Domain Exceptions to BaseException

_Migrate all domain-specific exceptions to extend `BaseException` so their messages are shown to API consumers._

### 2.1 RED: Write failing tests for domain exceptions ✅

**File**: [`tests/graphql/test_error_handler.py`](../../tests/graphql/test_error_handler.py)

**Test scenarios**:
- `test_does_not_mask_domain_exception` - Returns `False` for domain exceptions that now extend `BaseException` (using one representative exception per domain)

### 2.2 GREEN: Migrate domain exception base classes ✅

Change each domain exception base class from `Exception` to `BaseException`:

- [`app/graphql/pos/validations/exceptions.py`](../../app/graphql/pos/validations/exceptions.py) — `ValidationError(Exception)` → `ValidationError(BaseException)`
- [`app/graphql/pos/organization_alias/exceptions.py`](../../app/graphql/pos/organization_alias/exceptions.py) — `OrganizationAliasError(Exception)` → `OrganizationAliasError(BaseException)`
- [`app/graphql/pos/data_exchange/exceptions.py`](../../app/graphql/pos/data_exchange/exceptions.py) — `ExchangeFileError(Exception)` → `ExchangeFileError(BaseException)`
- [`app/graphql/pos/agreement/exceptions.py`](../../app/graphql/pos/agreement/exceptions.py) — `AgreementError(Exception)` → `AgreementError(BaseException)`
- [`app/graphql/pos/field_map/exceptions.py`](../../app/graphql/pos/field_map/exceptions.py) — `FieldMapError(Exception)` → `FieldMapError(BaseException)`
- [`app/graphql/settings/organization_preferences/exceptions.py`](../../app/graphql/settings/organization_preferences/exceptions.py) — `OrganizationPreferenceError(Exception)` → `OrganizationPreferenceError(BaseException)`
- [`app/graphql/connections/exceptions.py`](../../app/graphql/connections/exceptions.py) — `UserNotFoundError(Exception)` and `UserOrganizationRequiredError(Exception)` → extend `BaseException`, refactor constructors to call `super().__init__(message)`

### 2.3 VERIFY: Run task all ✅

Run `task all` to confirm all checks pass.

---

## Phase 3: Verification

_Manual verification that error messages are properly displayed._

### 3.1 Unit test verification ✅

All 10 unit tests pass, covering:
- `BaseException` subclasses (e.g., `RemoteApiError`) → message shown ✅
- Non-custom exceptions (e.g., `ValueError`) → masked as "Unexpected error." ✅
- GraphQL errors without `original_error` (e.g., syntax errors) → message shown as-is ✅
- 7 domain exceptions (one per domain) → message shown after migration ✅

### 3.2 Manual testing ⏸️

Manual testing against the local server was blocked by a local environment issue: `Tenant app not found` from `commons/db/controller.py`. Requests fail before reaching the service layer, so domain exceptions cannot be triggered. This is unrelated to the error handler changes.

Verification is accepted based on unit test coverage. Full manual testing can be performed once the application is deployed to a configured environment.

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns |
| 2 | Effects on other features | ✅ No negative effects |
| 3 | Code quality issues | ✅ Clean |
| 4 | Potential bugs | ✅ None found |
| 5 | Commit messages | ✅ Single-line, correct format |
| 6 | No Co-Authored-By | ✅ Fixed — removed from commit `31e7df0` |
| 7 | Document updates | ✅ Fixed — Results table reverted to TBD |

---

## Results

| Metric         | Value |
|----------------|-------|
| Phases         | 3     |
| Files Created  | 2     |
| Files Modified | 10    |
| Tests Added    | 10    |
