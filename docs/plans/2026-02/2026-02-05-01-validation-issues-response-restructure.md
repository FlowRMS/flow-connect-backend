# Validation Issues Response Restructure

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1570](https://linear.app/flow-labs/issue/FLO-1570/validation-issues-response-restructure)
- **Created**: 2026-02-05 00:33 -03
- **Approved**: 2026-02-05 08:56 -03
- **Finished**: 2026-02-05 14:16 -03
- **PR**: [#35](https://github.com/FlowRMS/flow-py-connect/pull/35), [#38](https://github.com/FlowRMS/flow-py-connect/pull/38)
- **Commit Prefix**: Validation Issues Restructure

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: Rename Groups, Add FYI, Remove Redundant validationType](#phase-1-rename-groups-add-fyi-remove-redundant-validationtype)
- [Phase 2: Add ValidationKey Grouping](#phase-2-add-validationkey-grouping)
- [Phase 3: Verification](#phase-3-verification)
- [GraphQL API Changes](#graphql-api-changes)
- [Review](#review)
- [Changes During Testing](#changes-during-testing)
- [Results](#results)

---

## Overview

Restructure the `FileValidationIssuesResponse` GraphQL response to:

1. **Rename groups**: `standardValidation` → `blocking`, `validationWarning` → `warning`
2. **Add new group**: `fyi` (always empty for now, no validation keys map to it)
3. **Add file-level grouping**: Within each type group, issues are sub-grouped by file
4. **Add validationKey grouping**: Within each file group, issues are sub-grouped by their `validationKey`

### Current Structure

```graphql
FileValidationIssueLiteResponse {
  id: ID!
  rowNumber: Int!
  title: String!
  columnName: String
  validationType: ValidationTypeEnum!  # REDUNDANT (implied by group)
  fileId: ID!
  fileName: String!
}

FileValidationIssuesResponse {
  standardValidation: ValidationIssueGroupResponse {
    items: [FileValidationIssueLiteResponse]
    count: Int
  }
  validationWarning: ValidationIssueGroupResponse {
    items: [FileValidationIssueLiteResponse]
    count: Int
  }
}
```

### Target Structure

```graphql
FileValidationIssueLiteResponse {
  id: ID!
  rowNumber: Int!
  title: String!
  columnName: String
  fileId: ID!                               # validationType REMOVED
  fileName: String!
}

FileValidationIssuesResponse {
  blocking: ValidationIssueGroupResponse {  # RENAMED from standardValidation
    items: [FileValidationIssueLiteResponse]
    count: Int
    files: [FileGroupResponse]              # NEW — grouped by file
  }
  warning: ValidationIssueGroupResponse {   # RENAMED from validationWarning
    items: [FileValidationIssueLiteResponse]
    count: Int
    files: [FileGroupResponse]              # NEW
  }
  fyi: ValidationIssueGroupResponse {       # NEW (always empty)
    items: [FileValidationIssueLiteResponse]
    count: Int
    files: [FileGroupResponse]              # NEW
  }
}

# NEW TYPE — groups issues by file within a validation type
FileGroupResponse {
  fileId: ID!
  fileName: String!
  items: [FileValidationIssueLiteResponse]
  count: Int!
  groups: [ValidationKeyGroupResponse]      # validationKey groups within this file
}

# NEW TYPE — groups issues by validationKey within a file
ValidationKeyGroupResponse {
  validationKey: String!
  title: String!
  items: [FileValidationIssueLiteResponse]
  count: Int!
}
```

---

## Design Decisions

### DD-1: Consolidate duplicate ValidationTypeEnum

**Decision**: Remove the inline `ValidationTypeEnum` from `file_validation_issue_types.py` and use the one from `validation_rule_types.py` (which wraps the model's `ValidationType` StrEnum).

- Currently two separate enum definitions exist: one in `file_validation_issue_types.py` (2 values) and one in `validation_rule_types.py` (3 values, wrapping the model)
- The model enum is the source of truth
- Consolidating avoids drift between the two

### DD-2: Keep ValidationType enum unchanged, map to response groups

**Decision**: The `ValidationType` StrEnum (`STANDARD_VALIDATION`, `VALIDATION_WARNING`, `AI_POWERED_VALIDATION`) stays as-is. The response group names are a mapping at the response level only.

- `ValidationType.STANDARD_VALIDATION` → `blocking` group
- `ValidationType.VALIDATION_WARNING` → `warning` group
- `ValidationType.AI_POWERED_VALIDATION` → `fyi` group (empty for now)
- The enum is used extensively across validators and VALIDATION_RULES — renaming would be high blast radius with no benefit

### DD-3: Remove validationType field from issue response types

**Decision**: Remove the `validationType` field from `FileValidationIssueLiteResponse` and `FileValidationIssueResponse`. Since issues are grouped by type in the response, the field is redundant. Keep `ValidationTypeEnum` in GraphQL only for `ValidationRuleResponse`.

- The validation type is already implicit from which group the issue belongs to
- Eliminates the duplicate `ValidationTypeEnum` in `file_validation_issue_types.py` (DD-1) since it's no longer needed there

### DD-4: Keep flat items alongside groups

**Decision**: Each group level keeps an `items` flat list alongside its sub-groups. `ValidationIssueGroupResponse` has `items` + `files`, `FileGroupResponse` has `items` + `groups`. The `items` field provides simple access at each level, while the nested grouping enables drill-down.

### DD-5: ValidationKeyGroupResponse title derivation

**Decision**: The `title` field in `ValidationKeyGroupResponse` is derived from the `validationKey` using the existing `get_issue_title()` function with `column_name=None` (column-agnostic title).

---

## Critical Files

| File | Action | Phase |
|------|--------|-------|
| `app/graphql/pos/validations/strawberry/file_validation_issue_types.py` | Modify | 1, 2 |
| `app/graphql/pos/validations/services/file_validation_issue_service.py` | Modify | 1, 2 |
| `app/graphql/pos/validations/queries/file_validation_issue_queries.py` | Modify | 1, 2 |
| `schema.graphql` | Modify | 1, 2 |
| `tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py` | Modify | 1, 2 |
| `tests/graphql/pos/validations/services/test_file_validation_issue_service.py` | Modify | 1, 2 |

---

## Phase 1: Rename Groups, Add FYI, Remove Redundant validationType

Rename response groups, add `fyi` group, and remove the redundant `validationType` field from issue response types. Follow TDD Red-Green-Refactor.

### 1.1 RED: Update tests for renamed groups and removed validationType ✅

- Update `test_file_validation_issue_queries.py`:
  - Change grouped response assertions from `standard_validation`/`validation_warning` to `blocking`/`warning`/`fyi`
  - Remove `validation_type` assertions from `FileValidationIssueLiteResponse` and `FileValidationIssueResponse` tests
- Update `test_file_validation_issue_service.py`: add `AI_POWERED_VALIDATION` (fyi) group to expected results

### 1.2 GREEN: Implement changes ✅

- **`strawberry/file_validation_issue_types.py`**:
  - Remove inline `ValidationTypeEnum` (DD-1, DD-3)
  - Remove `validation_type` field from `FileValidationIssueLiteResponse` and `FileValidationIssueResponse`
  - Remove `validation_type` derivation logic from `from_model()` methods
  - Rename `FileValidationIssuesResponse` fields to `blocking`, `warning`, `fyi`
- **`services/file_validation_issue_service.py`**: Add `AI_POWERED_VALIDATION` key to grouped dict (empty, maps to `fyi`)
- **`queries/file_validation_issue_queries.py`**: Update field names, add fyi group construction
- **`schema.graphql`**: Regenerate after changes

### 1.3 REFACTOR: Clean up ✅

- Remove unused imports
- Verify `task all` passes

---

## Phase 2: Add ValidationKey Grouping

Add sub-grouping by `validationKey` within each validation type group. Follow TDD Red-Green-Refactor.

### 2.1 RED: Write tests for validationKey grouping ✅

- Add test for `ValidationKeyGroupResponse` type
- Add test for grouped response structure with `groups` field
- Add service test for grouping by key within each type

### 2.2 GREEN: Implement validationKey grouping ✅

- **`strawberry/file_validation_issue_types.py`**: Add `ValidationKeyGroupResponse` type. Add `groups` field to `ValidationIssueGroupResponse`
- **`services/file_validation_issue_service.py`**: Return nested grouping: `dict[ValidationType, dict[str, list[FileValidationIssue]]]`
- **`queries/file_validation_issue_queries.py`**: Build `groups` list from service response
- **`schema.graphql`**: Regenerate after changes

### 2.3 REFACTOR: Clean up ✅

- Verify file lengths under 300 lines
- Remove redundancy
- Verify `task all` passes

---

## Phase 3: Verification

Run full verification and finalize.

### 3.1 Run `task all` ✅

- Type checks (basedpyright)
- Linting (ruff)
- All tests pass

### 3.2 Schema verification ✅

- Regenerate `schema.graphql`
- Verify it matches expected target structure

### 3.3 Manual testing ✅

| # | Test Case | Query | Expected | Result |
|---|-----------|-------|----------|--------|
| 1 | List query returns new group structure | `fileValidationIssues { blocking { count files { ... } } warning { ... } fyi { ... } }` | `blocking`, `warning`, `fyi` groups present; `fyi` empty | ✅ All groups present, fyi empty |
| 2 | Files contain validationKey sub-groups | Check `files → groups` inside `blocking` | Each file has `fileId`, `fileName`, `groups`; each group has `validationKey`, `title`, `items`, `count` | ✅ Schema resolves all nested fields (no pending issues in DB) |
| 3 | `validationType` field removed from items | Request `validationType` on issue items | GraphQL error (field does not exist) | ✅ `Cannot query field 'validationType' on type 'FileValidationIssueLiteResponse'` |
| 4 | Single issue detail query works | `fileValidationIssue(id: "...")` | Returns issue without `validationType` field | ✅ Returns null for missing ID; `validationType` rejected on detail type |

---

## GraphQL API Changes

_Breaking and non-breaking changes to the GraphQL schema._

| Change | Type | Detail |
|--------|------|--------|
| `FileValidationIssueLiteResponse.validationType`: removed | ⚠️ Breaking | Redundant — type implied by group (DD-3) |
| `FileValidationIssueResponse.validationType`: removed | ⚠️ Breaking | Redundant — type implied by group (DD-3) |
| `FileValidationIssuesResponse.standardValidation` → `blocking` | ⚠️ Breaking | Field renamed |
| `FileValidationIssuesResponse.validationWarning` → `warning` | ⚠️ Breaking | Field renamed |
| `ValidationTypeEnum` type: removed | ⚠️ Breaking | No longer needed after field removal |
| `FileValidationIssuesResponse.fyi`: added | ✅ Non-breaking | New group (always empty for now) |
| `ValidationIssueGroupResponse.files`: added | ✅ Non-breaking | New file-level grouping field (CH-1) |
| `ValidationIssueGroupResponse.groups`: removed | ⚠️ Breaking | Replaced by `files` → `groups` hierarchy (CH-1) |
| `FileGroupResponse` type: added | ✅ Non-breaking | New type for file-level grouping (CH-1) |
| `ValidationKeyGroupResponse` type: added | ✅ Non-breaking | New type for key-based sub-grouping |

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns |
| 2 | Effects on other features | ✅ No negative effects |
| 3 | Code quality issues | ✅ Clean |
| 4 | Potential bugs | ✅ None found |
| 5 | Commit messages | ✅ Single-line, correct format |
| 6 | No Co-Authored-By | ✅ None found |
| 7 | Breaking changes | ✅ Documented in GraphQL API Changes |
| 8 | Document updates | ✅ Updated GraphQL API Changes with CH-1 breaking change |

---

## Changes During Testing

_Issues discovered and fixed during testing/review. Prefixes: BF = bugfix, CH = behavior change._

### CH-1: Add file-level grouping within validation type groups

**Problem**: Issues from different pending files are mixed together in the same `validationKey` group. If `sales_jan.csv` and `sales_feb.csv` both have `required_field` issues, they appear in the same group with no file separation.

**Files**:
- `app/graphql/pos/validations/strawberry/file_validation_issue_types.py` - Add `FileGroupResponse`, replace `groups` with `files` on `ValidationIssueGroupResponse`
- `app/graphql/pos/validations/services/file_validation_issue_service.py` - Return 3-level grouping: `ValidationType` → `file_id` → `validation_key`
- `app/graphql/pos/validations/queries/file_validation_issue_queries.py` - Build `files` → `groups` hierarchy
- `schema.graphql` - Regenerate
- `tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py` - Update for new structure
- `tests/graphql/pos/validations/services/test_file_validation_issue_service.py` - Update for 3-level grouping

**Change**: Add a `FileGroupResponse` type between `ValidationIssueGroupResponse` and `ValidationKeyGroupResponse`. The hierarchy becomes: `blocking/warning/fyi` → `files` (by file) → `groups` (by validationKey). Follow TDD Red-Green-Refactor.

#### CH-1.1 RED: Update tests for file-level grouping ✅

- Update service tests: expect `dict[ValidationType, dict[UUID, dict[str, list]]]`
- Update query type tests: `ValidationIssueGroupResponse` has `files` instead of `groups`
- Add `FileGroupResponse` type test
- Add query test with issues from multiple files

#### CH-1.2 GREEN: Implement file-level grouping ✅

- **`strawberry/file_validation_issue_types.py`**: Add `FileGroupResponse` type. Replace `groups` with `files` on `ValidationIssueGroupResponse`
- **`services/file_validation_issue_service.py`**: Return `dict[ValidationType, dict[UUID, dict[str, list[FileValidationIssue]]]]`
- **`queries/file_validation_issue_queries.py`**: Build `files` → `groups` hierarchy from service response
- **`schema.graphql`**: Regenerate

#### CH-1.3 REFACTOR: Clean up ✅

- Verify file lengths under 300 lines
- Verify `task all` passes (408 tests, 0 type errors, 0 lint issues)

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~5h 20m (08:56 → 14:16) |
| Phases | 3 + CH-1 |
| Files Modified | 7 |
| Tests Added | 8 |
