# Filtered Validation Issues Query

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1606](https://linear.app/flow-labs/issue/FLO-1606/filtered-validation-issues-query)
- **Created**: 2026-02-05 15:39 -03
- **Approved**: 2026-02-05 15:54 -03
- **Finished**: 2026-02-05 20:38 -03
- **PR**: [#39](https://github.com/FlowRMS/flow-py-connect/pull/39)
- **Commit Prefix**: Filtered Validation Issues

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: Repository Layer](#phase-1-repository-layer)
- [Phase 2: Service Layer](#phase-2-service-layer)
- [Phase 3: GraphQL Query Layer](#phase-3-graphql-query-layer)
- [Phase 4: Verification](#phase-4-verification)
- [GraphQL API Changes](#graphql-api-changes)
- [Review](#review)
- [Results](#results)

---

## Overview

Add a new GraphQL query `filteredFileValidationIssues` that returns a flat list of `FileValidationIssueResponse` items filtered by `ValidationType`, `fileId`, and `validationKey`.

This is a **drill-down query** for the validation issues view. The existing `fileValidationIssues` query returns a grouped overview with lite response items (no `message`, `validation_key`, or `row_data`). When a user clicks on a specific validation key group within a file, this new query provides the full issue details for that combination.

**GraphQL Schema**:

```graphql
filteredFileValidationIssues(
  validationType: ValidationType!
  fileId: ID!
  validationKey: String!
): [FileValidationIssueResponse!]!
```

---

## Design Decisions

### DD-1: All three filter parameters are required

**Decision**: `validationType`, `fileId`, and `validationKey` are all required parameters.

- This query serves a specific UI drill-down use case: user clicks on a group (type + file + key) and sees full details
- Required parameters enforce the intended usage and simplify implementation
- If broader filtering is needed later, a separate query with optional parameters can be added (non-breaking)

### DD-2: ValidationType used as a consistency guard, not a SQL filter

**Decision**: ValidationType is validated in the service layer against the validation_key, not used as a SQL column filter.

- ValidationType is not stored in the database; it's derived from the validation_key
- Each validation_key belongs to exactly one ValidationType (blocking vs warning)
- The service validates that the provided validationType matches the validation_key's actual type
- If they don't match, the query returns an empty list (no error) - consistent with a "no results" scenario

### DD-3: Scoped to pending files only

**Decision**: The query only returns issues for files with `PENDING` status, matching the existing `fileValidationIssues` query behavior.

- Consistency with the existing grouped query
- Pending files are the only ones with actionable validation issues

---

## Critical Files

| File | Action | Description |
|------|--------|-------------|
| `app/graphql/pos/validations/repositories/file_validation_issue_repository.py` | M | Add `get_by_file_and_key` method |
| `app/graphql/pos/validations/services/file_validation_issue_service.py` | M | Add `get_filtered_issues` method |
| `app/graphql/pos/validations/queries/file_validation_issue_queries.py` | M | Add `filtered_file_validation_issues` resolver |
| `schema.graphql` | M | Add new query definition |
| `tests/graphql/pos/validations/repositories/test_file_validation_issue_repository.py` | M | Add repository tests |
| `tests/graphql/pos/validations/services/test_file_validation_issue_service.py` | M | Add service tests |
| `tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py` | M | Add query resolver tests |

---

## Phase 1: Repository Layer

Add a new repository method that filters validation issues by exchange_file_id and validation_key for pending files.

### 1.1 RED: Tests for `get_by_file_and_key` ✅

**File**: `tests/graphql/pos/validations/repositories/test_file_validation_issue_repository.py`

Test scenarios:
- Returns issues matching file_id and validation_key for pending files
- Returns empty list when no issues match
- Only returns issues for pending files (excludes non-pending)
- Orders results by row_number
- Eagerly loads exchange_file relationship

### 1.2 GREEN: Implement `get_by_file_and_key` ✅

**File**: `app/graphql/pos/validations/repositories/file_validation_issue_repository.py`

New method: `get_by_file_and_key(exchange_file_id: uuid.UUID, validation_key: str) -> list[FileValidationIssue]`

- Join with ExchangeFile to filter by pending status
- Filter by exchange_file_id and validation_key
- Eager load exchange_file relationship (needed for response mapping)
- Order by row_number

### 1.3 REFACTOR ✅

Run `task all` and clean up.

---

## Phase 2: Service Layer

Add a service method that validates the type/key consistency and delegates to the repository.

### 2.1 RED: Tests for `get_filtered_issues` ✅

**File**: `tests/graphql/pos/validations/services/test_file_validation_issue_service.py`

Test scenarios:
- Calls repository with correct file_id and validation_key when type matches
- Returns empty list when validationType does not match the validation_key's actual type
- Returns results from repository when type matches (blocking key + STANDARD_VALIDATION)
- Returns results from repository when type matches (warning key + VALIDATION_WARNING)

### 2.2 GREEN: Implement `get_filtered_issues` ✅

**File**: `app/graphql/pos/validations/services/file_validation_issue_service.py`

New method: `get_filtered_issues(validation_type: ValidationType, file_id: uuid.UUID, validation_key: str) -> list[FileValidationIssue]`

- Use existing `_get_validation_type` to check if the validation_key belongs to the requested type
- If mismatch, return empty list
- If match, call `repository.get_by_file_and_key(file_id, validation_key)`

### 2.3 REFACTOR ✅

Run `task all` and clean up.

---

## Phase 3: GraphQL Query Layer

Add the new query resolver and update the GraphQL schema.

### 3.1 RED: Tests for query resolver ✅

**File**: `tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py`

Test scenarios:
- Returns list of FileValidationIssueResponse with all fields mapped correctly
- Returns empty list when service returns no results
- Passes all parameters through to the service correctly

### 3.2 GREEN: Implement query resolver ✅

**File**: `app/graphql/pos/validations/queries/file_validation_issue_queries.py`

New resolver method on `FileValidationIssueQueries`:
```
filtered_file_validation_issues(validationType, fileId, validationKey) -> [FileValidationIssueResponse]
```

- Accept `validation_type: ValidationType`, `file_id: strawberry.ID`, `validation_key: str`
- Convert file_id to UUID
- Call service.get_filtered_issues
- Map results to FileValidationIssueResponse via `from_model`

### 3.3 REFACTOR: Update schema.graphql ✅

Run `task export-schema` and `task all`.

---

## Phase 4: Verification

### 4.1 Run `task all` ✅

Ensure all checks pass: type checks, linting, tests.

### 4.2 Manual Testing

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Query with valid blocking type + file + key | Returns matching issues with full details | ✅ |
| 2 | Query with valid warning type + file + key | Returns matching warning issues | ⏸️ No warning data |
| 3 | Query with mismatched type/key | Returns empty list | ✅ |
| 4 | Query with non-existent fileId | Returns empty list | ✅ |

---

## GraphQL API Changes

_Breaking and non-breaking changes to the GraphQL schema._

| Change | Type | Detail |
|--------|------|--------|
| `Query.filteredFileValidationIssues(validationType, fileId, validationKey): [FileValidationIssueResponse!]!` | ✅ Non-breaking | New drill-down query for validation issues |

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns — query uses indexed columns with proper eager loading |
| 2 | Effects on other features | ✅ No negative effects — additive query, no changes to existing functionality |
| 3 | Code quality issues | ✅ Clean — follows established repository/service/query patterns |
| 4 | Potential bugs | ✅ None found — edge cases handled (type mismatch, non-existent file) |
| 5 | Commit messages | ✅ Single-line, correct format with commit prefix |
| 6 | No Co-Authored-By | ✅ None found in any of the 5 commits |
| 7 | Breaking changes | ✅ None — new query is additive |
| 8 | Document updates | ✅ Added GraphQL API Changes and Review sections |

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~2 hours |
| Phases | 4 |
| Files Modified | 7 |
| Tests Added | 9 |
