# Hotfix: Tenant Not Found Error Masked as "Unexpected error"

- **Status**: 🟢 Complete
- **Related Plan**: [GraphQL Error Handler](../../plans/2026-02/2026-02-03-01-graphql-error-handler.md)
- **Linear Task**: [FLO-1506](https://linear.app/flow-labs/issue/FLO-1506/hotfix-tenant-not-found-error-masked-as-unexpected-error)
- **Created**: 2026-02-03 13:30 -03
- **Approved**: 2026-02-03 17:00 -03
- **Finished**: 2026-02-03 17:30 -03
- **PR**: [#32](https://github.com/FlowRMS/flow-py-connect/pull/32)
- **Commit Prefix**: Tenant Error

---

## Table of Contents

- [Problem](#problem)
- [Cause](#cause)
- [Solution](#solution)
- [Files Changed](#files-changed)
- [Testing](#testing)
- [Review](#review)
- [Results](#results)

---

## Problem

When the multi-tenant database controller cannot find a tenant, it raises a plain `Exception("Tenant app not found")` from `commons/db/controller.py:215`. Because this is a plain `Exception` (not a subclass of our `BaseException`), the `should_mask_error` function in `app/graphql/error_handler.py` masks it, and the client receives `"Unexpected error."` instead of the actual message.

**Reproduction**: Send any authenticated GraphQL query when the user's tenant is not registered in the multi-tenant controller.

**Expected**: `"Tenant app not found"` (or a user-friendly equivalent)
**Actual**: `"Unexpected error."`

## Cause

The `commons` package (external dependency) raises a plain `Exception` at `controller.py:215`:
```python
raise Exception(f"Tenant {name} not found")
```

Our `should_mask_error` only allows `BaseException` subclasses through (Marker Interface pattern from the GraphQL Error Handler plan). Since the `commons` exception is a plain `Exception`, it gets masked.

The `create_session` function in `app/core/db/db_provider.py:19` calls `controller.scoped_session()` without catching this exception, so it propagates as-is to the error handler.

## Solution

Catch the plain `Exception` from the multi-tenant controller in `db_provider.py` and re-raise it as a `TenantNotFoundError` (a new `BaseException` subclass). This follows the same Marker Interface pattern established in the GraphQL Error Handler plan: wrap external exceptions at the boundary so they become user-facing errors.

1. Add `TenantNotFoundError` to `app/errors/common_errors.py`
2. Wrap `controller.scoped_session()` and `controller.transient_session()` in `db_provider.py` with a try/except that catches the tenant-not-found exception and re-raises as `TenantNotFoundError`

## Files Changed

| File | Change | Status |
|------|--------|--------|
| `app/errors/common_errors.py` | Add `TenantNotFoundError` class | ✅ |
| `app/core/db/db_provider.py` | Catch tenant exception, re-raise as `TenantNotFoundError` | ✅ |
| `tests/core/db/test_db_provider.py` | Tests for tenant-not-found wrapping | ✅ |

_Status: ⬜ = Pending, ✅ = Complete_

## Testing

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Unit: `create_session` raises `TenantNotFoundError` | `TenantNotFoundError` with original message | ✅ |
| 2 | Unit: `create_transient_session` raises `TenantNotFoundError` | `TenantNotFoundError` with original message | ✅ |
| 3 | Unit: Other exceptions not caught | `RuntimeError` propagates as-is | ✅ |
| 4 | Manual: curl returns tenant error message | `"Tenant app not found"` | ✅ |

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns — only adds a try/except at session creation boundary |
| 2 | Effects on other features | ✅ No negative effects — only catches tenant-not-found, all other exceptions propagate unchanged |
| 3 | Code quality issues | ✅ Clean — pattern matching on `"not found"` is broad but matches the `commons` package convention |
| 4 | Potential bugs | ✅ None found |
| 5 | Commit messages | ✅ Single-line, correct format |
| 6 | No Co-Authored-By | ✅ None found |
| 7 | Document updates | ✅ No changes needed |

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~30 min |
| Commits | 3 |
| Files Modified | 2 (`db_provider.py`, `common_errors.py`) |
| Files Created | 2 (`test_db_provider.py`, `tests/core/db/__init__.py`) |
| Tests Added | 3 |