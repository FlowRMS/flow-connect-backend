# Send Pending Exchange Files

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1472](https://linear.app/flow-labs/issue/FLO-1472/send-data)
- **Created**: 2026-02-02 09:24 -03
- **Approved**: 2026-02-02 10:28 -03
- **Finished**: 2026-02-02 22:36 -03
- **PR**: [#29](https://github.com/FlowRMS/flow-py-connect/pull/29)
- **Commit Prefix**: Send Pending Files

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: Create Send Mutation](#phase-1-create-send-mutation)
- [Phase 2: Verification](#phase-2-verification)
- [Changes During Testing](#changes-during-testing)
- [Results](#results)

---

## Overview

Create a GraphQL mutation to send all pending exchange files to target organizations. The mutation will:

1. **Validate before sending**: Check that no pending files have `STANDARD_VALIDATION` issues (blocking validation errors)
2. **Change status**: Update all pending files from `PENDING` to `SENT`
3. **Preserve issues**: Validation issues are NOT removed - they remain for audit purposes

**Business Rule**: Files can only be sent when ALL pending files have passed standard validation. If any file has blocking validation issues, the entire send operation fails.

**Note**: The `fileValidationIssues` query already filters by pending files (via `get_pending_issues_grouped()`), so no changes needed there.

---

## Design Decisions

### DD-1: Mutation Naming Convention

**Decision**: Use `sendPendingExchangeFiles` (verb in present tense) instead of `sentPendingExchangeFiles`.

- GraphQL mutations should use imperative/present tense verbs
- Consistent with existing mutations: `uploadExchangeFiles`, `deleteExchangeFile`
- Clear action-oriented naming

### DD-2: All-or-Nothing Send Behavior

**Decision**: Send operation is atomic - either all pending files are sent, or none are.

- Simplifies validation logic: check once, apply to all
- Prevents partial sends that could confuse data reconciliation
- User can delete problematic files individually if needed

### DD-3: Return Type and Error Handling

**Decision**: Return `SendPendingFilesResponse` with `success: bool` and `files_sent: int`. Throw exceptions for error cases.

- Success response provides count of files sent
- Errors follow existing pattern: custom exceptions in `exceptions.py`
- New exception: `HasBlockingValidationIssuesError` - raised when pending files have STANDARD_VALIDATION issues
- New exception: `NoPendingFilesError` - raised when no pending files exist to send

### DD-4: Transactional Safety

**Decision**: The entire send operation runs within a single database transaction.

- Repository uses `flush()` not `commit()` - transaction managed at session level
- If any status update fails, the entire transaction rolls back
- No partial state possible (e.g., 2 of 3 files sent)
- Future-proof: if sending evolves (e.g., email), we can extend with saga pattern or outbox pattern

---

## Critical Files

| File | Status | Description |
|------|--------|-------------|
| [`app/graphql/pos/data_exchange/exceptions.py`](../../app/graphql/pos/data_exchange/exceptions.py) | ✅ | Add new exceptions |
| [`app/graphql/pos/data_exchange/mutations/exchange_file_mutations.py`](../../app/graphql/pos/data_exchange/mutations/exchange_file_mutations.py) | ✅ | Add send mutation |
| [`app/graphql/pos/data_exchange/services/exchange_file_service.py`](../../app/graphql/pos/data_exchange/services/exchange_file_service.py) | ✅ | Add send_pending_files method |
| [`app/graphql/pos/data_exchange/repositories/exchange_file_repository.py`](../../app/graphql/pos/data_exchange/repositories/exchange_file_repository.py) | ✅ | Add update_pending_to_sent method |
| [`app/graphql/pos/data_exchange/strawberry/exchange_file_types.py`](../../app/graphql/pos/data_exchange/strawberry/exchange_file_types.py) | ✅ | Add response type |
| [`app/graphql/pos/validations/repositories/file_validation_issue_repository.py`](../../app/graphql/pos/validations/repositories/file_validation_issue_repository.py) | ✅ | Add has_blocking_issues method |
| [`tests/graphql/pos/data_exchange/test_send_pending_files.py`](../../tests/graphql/pos/data_exchange/test_send_pending_files.py) | ✅ | Unit tests |

---

## Phase 1: Create Send Mutation

_Implement the mutation to send pending exchange files with validation check._

### 1.1 RED: Write failing tests for service method ✅

**File**: [`tests/graphql/pos/data_exchange/test_send_pending_files.py`](../../tests/graphql/pos/data_exchange/test_send_pending_files.py)

**Test scenarios**:
- `test_send_pending_files_success` - Returns count when no blocking issues exist
- `test_send_pending_files_with_blocking_issues` - Raises `HasBlockingValidationIssuesError`
- `test_send_pending_files_no_pending` - Raises `NoPendingFilesError` when no files to send

### 1.2 GREEN: Add exceptions ✅

**File**: [`app/graphql/pos/data_exchange/exceptions.py`](../../app/graphql/pos/data_exchange/exceptions.py)

Add two new exceptions extending `ExchangeFileError`:
- `HasBlockingValidationIssuesError` - Cannot send files with blocking validation issues
- `NoPendingFilesError` - No pending files to send

### 1.3 GREEN: Implement blocking issue check ✅

**File**: [`app/graphql/pos/validations/repositories/file_validation_issue_repository.py`](../../app/graphql/pos/validations/repositories/file_validation_issue_repository.py)

Add method `has_blocking_issues_for_pending_files(org_id) -> bool` that checks if any pending files have STANDARD_VALIDATION issues.

### 1.4 GREEN: Implement repository method ✅

**File**: [`app/graphql/pos/data_exchange/repositories/exchange_file_repository.py`](../../app/graphql/pos/data_exchange/repositories/exchange_file_repository.py)

Add method `update_pending_to_sent(org_id) -> int` that updates all pending files to SENT status and returns count of updated files.

### 1.5 GREEN: Implement service method ✅

**File**: [`app/graphql/pos/data_exchange/services/exchange_file_service.py`](../../app/graphql/pos/data_exchange/services/exchange_file_service.py)

Add method `send_pending_files() -> int` that:
1. Checks for blocking validation issues (raises `HasBlockingValidationIssuesError` if any)
2. Updates all pending files to SENT status
3. Raises `NoPendingFilesError` if no pending files exist
4. Returns count of files sent

### 1.6 GREEN: Add response type and mutation ✅

**File**: [`app/graphql/pos/data_exchange/strawberry/exchange_file_types.py`](../../app/graphql/pos/data_exchange/strawberry/exchange_file_types.py)

Add `SendPendingFilesResponse` type with fields: `success: bool`, `files_sent: int`

**File**: [`app/graphql/pos/data_exchange/mutations/exchange_file_mutations.py`](../../app/graphql/pos/data_exchange/mutations/exchange_file_mutations.py)

Add mutation `send_pending_exchange_files` that calls service and returns `SendPendingFilesResponse`

### 1.7 REFACTOR: Clean up and verify ✅

- Type checking: 0 errors ✅
- Lint: passes ✅
- Tests: 356 passed (1 pre-existing failure on main) ✅
- Schema exported with new mutation ✅

---

## Phase 2: Verification

_Manual testing and integration verification._

### 2.1 Schema verification ✅

- Mutation `sendPendingExchangeFiles` appears in schema.graphql ✅
- Returns `SendPendingFilesResponse` with `success: Boolean!` and `filesSent: Int!` ✅

### 2.2 Manual testing

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Call `sendPendingExchangeFiles` with no pending files | `NoPendingFilesError` | ✅ |
| 2 | Upload file with blocking validation issues, then call mutation | `HasBlockingValidationIssuesError` | ⏸️ |
| 3 | Upload valid file (no blocking issues), then call mutation | `{ success: true, filesSent: N }` | ✅ |
| 4 | After successful send, query `pendingExchangeFiles` | Empty list | ✅ |

**Note on Test 2**: Cannot be manually tested because:
1. Async validation task (`trigger_validation_task`) doesn't run in the current server setup
2. Multi-tenant database architecture prevents direct insertion of test data

This code path is fully covered by unit test `test_send_pending_files_with_blocking_issues`.

### 2.3 Update plan with file links ✅

- All Critical Files updated with links and ✅ marks (done in Phase 1)

---

## Changes During Testing

_Issues discovered and fixed during testing/review._

### BF-1: Alembic multiple heads ✅

**Problem**: Migration command failed with "multiple heads" error - two migration files had the same revision ID `20260130_001`.
**Files**:
- [`alembic/versions/20260130_merge_heads.py`](../../alembic/versions/20260130_merge_heads.py) - Fixed down_revision to merge correct heads
- [`alembic/versions/20260130_add_field_map_direction.py`](../../alembic/versions/20260130_add_field_map_direction.py) - Changed revision to `20260130_002`
**Fix**: Renamed duplicate revision and corrected merge dependencies.

### CH-1: TDD standards - manual testing format ✅

**Problem**: No standard format for documenting manual test results in plans.
**File**: [`docs/methodologies/tdd-standards.md`](../../docs/methodologies/tdd-standards.md)
**Change**: Added table format with status markers (✅, ⏸️, ❌) for manual testing documentation.

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~13 hours |
| Phases | 2 |
| Files Modified | 12 |
| Tests Added | 3 |