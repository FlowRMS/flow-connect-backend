# Query to Get Validation Issues

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1357](https://linear.app/flow-labs/issue/FLO-1357/query-to-get-the-list-of-issues)
- **Created**: 2026-01-28 12:44 -03
- **Approved**: 2026-01-28 14:05 -03
- **Finished**: 2026-01-30 14:38 -03
- **PR**: [#25](https://github.com/FlowRMS/flow-py-connect/pull/25)
- **Commit Prefix**: Validation Issues Query

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: DB Schema](#phase-1-db-schema)
- [Phase 2: Update Validation Pipeline](#phase-2-update-validation-pipeline)
- [Phase 3: Title Mapping & Service](#phase-3-title-mapping--service)
- [Phase 4: GraphQL Layer](#phase-4-graphql-layer)
- [Phase 5: Verification](#phase-5-verification)
- [Results](#results)

---

## Overview

When a file is uploaded and validated, it generates a list of issues. We need GraphQL queries to:

1. **List Issues Query**: Get all issues across **all pending files** (`ExchangeFileStatus.PENDING`), grouped by type (`ValidationType`). Each issue includes file info (file_id, file_name).
2. **Get Issue by ID Query**: Get a single issue with the affected row values from the file

### Current State

- `FileValidationIssue` model stores: `exchange_file_id`, `row_number`, `column_name`, `validation_key`, `message`
- `ValidationType` enum: `STANDARD_VALIDATION`, `VALIDATION_WARNING`, `AI_POWERED_VALIDATION`
- Existing query `file_validation_issues(exchange_file_id)` returns a flat list
- **Missing**: Row values are NOT currently stored - only `row_number`

### Key Files

| File | Purpose |
|------|---------|
| `app/graphql/pos/validations/models/file_validation_issue.py` | Model |
| `app/graphql/pos/validations/queries/file_validation_issue_queries.py` | Current query |
| `app/graphql/pos/validations/strawberry/file_validation_issue_types.py` | Response types |
| `app/graphql/pos/validations/repositories/file_validation_issue_repository.py` | Repository |

---

## Design Decisions

### DD-1: Affected Rows Storage

**Decision**: Store row values as `row_data: JSONB` during validation.

- Stores original row values at validation time
- Future editing feature can add `corrected_data: JSONB` column later
- Fast retrieval, no dependency on S3 file availability

### DD-2: Query Response Structure

**Decision**: Pre-grouped nested structure by `ValidationType`, across all pending files.

```graphql
query {
  fileValidationIssues {
    standardValidation {
      items { id, title, fileName, fileId, rowNumber, columnName }
      count
    }
    validationWarning {
      items { ... }
      count
    }
  }
}
```

- No `fileId` parameter - returns issues from **all files** with `status = PENDING`
- Each issue includes `fileId` and `fileName` to identify the source file

### DD-3: Title and Description Fields

**Decision**: Derive from `validation_key` + `column_name` using a mapping dict.

Examples:
- `required_field` + `selling_branch_zip` → "Selling branch zip code missing"
- `required_field` + `product_identifier` → "No product identifier found"
- `zip_code` + `selling_branch_zip` → "Invalid ZIP code format"

Mapping dict `(validation_key, column_name) → title` for explicit control over titles.

---

## Critical Files

| File | Status | Description |
|------|--------|-------------|
| [`app/graphql/pos/validations/models/file_validation_issue.py`](../../app/graphql/pos/validations/models/file_validation_issue.py) | ✅ | Add `row_data` column |
| [`alembic/versions/20260128_add_row_data_to_file_validation_issues.py`](../../alembic/versions/20260128_add_row_data_to_file_validation_issues.py) | ✅ | Migration |
| [`app/graphql/pos/validations/services/validation_execution_service.py`](../../app/graphql/pos/validations/services/validation_execution_service.py) | ✅ | Pass row data to issues |
| [`app/graphql/pos/validations/constants.py`](../../app/graphql/pos/validations/constants.py) | ✅ | Title mapping dict |
| [`app/graphql/pos/validations/services/file_validation_issue_service.py`](../../app/graphql/pos/validations/services/file_validation_issue_service.py) | ✅ | New service |
| [`app/graphql/pos/validations/repositories/file_validation_issue_repository.py`](../../app/graphql/pos/validations/repositories/file_validation_issue_repository.py) | ✅ | Add get_by_id, get_by_pending_files |
| [`app/graphql/pos/validations/strawberry/file_validation_issue_types.py`](../../app/graphql/pos/validations/strawberry/file_validation_issue_types.py) | ✅ | New response types |
| [`app/graphql/pos/validations/queries/file_validation_issue_queries.py`](../../app/graphql/pos/validations/queries/file_validation_issue_queries.py) | ✅ | New queries |

---

## Phase 1: DB Schema

_Add `row_data` JSONB column to store original row values._

### 1.1 GREEN: Add column and relationship to model ✅

**File**: [`app/graphql/pos/validations/models/file_validation_issue.py`](../../app/graphql/pos/validations/models/file_validation_issue.py)

Added:
- `row_data: Mapped[dict[str, Any] | None]` - JSONB, nullable, default=None
- `exchange_file: Mapped[ExchangeFile]` - Relationship for eager loading file info

### 1.2 GREEN: Create migration ✅

**File**: [`alembic/versions/20260128_add_row_data_to_file_validation_issues.py`](../../alembic/versions/20260128_add_row_data_to_file_validation_issues.py)

- Added `row_data` JSONB column to `connect_pos.file_validation_issues` table

### 1.3 VERIFY: Run `task all` ✅

All checks passed.

---

## Phase 2: Update Validation Pipeline

_Modify validation to store row data when creating issues._

### 2.1 RED: Write failing tests for row data storage ✅

**File**: [`tests/graphql/pos/validations/services/test_validation_execution_service.py`](../../tests/graphql/pos/validations/services/test_validation_execution_service.py)

**Test scenarios**:
- `test_validation_issue_includes_row_data` - Issue created with row data populated containing all columns

### 2.2 GREEN: Update ValidationIssue dataclass ✅

**File**: [`app/graphql/pos/validations/services/validators/base.py`](../../app/graphql/pos/validations/services/validators/base.py)

Added `row_data: dict[str, Any] | None = field(default=None)` to `ValidationIssue` dataclass.

### 2.3 GREEN: Update validators to include row data ✅

**Files**: All 10 validator files in `app/graphql/pos/validations/services/validators/`

Added `row_data=row.data` when creating `ValidationIssue` instances.

### 2.4 GREEN: Update ValidationExecutionService ✅

**File**: [`app/graphql/pos/validations/services/validation_execution_service.py`](../../app/graphql/pos/validations/services/validation_execution_service.py)

Added `row_data=issue.row_data` when creating `FileValidationIssue` models.

### 2.5 VERIFY: Run `task all` ✅

All checks passed. 6 tests pass.

---

## Phase 3: Title Mapping & Service

_Create title mapping and service for querying issues._

### 3.1 RED: Write failing tests for title derivation ✅

**File**: [`tests/graphql/pos/validations/test_issue_title_mapping.py`](../../tests/graphql/pos/validations/test_issue_title_mapping.py)

**Test scenarios**:
- `test_required_field_selling_branch_zip_title` - Returns "Selling branch zip code missing"
- `test_required_field_product_identifier_title` - Returns "No product identifier found"
- `test_zip_code_validation_title` - Returns "Invalid ZIP code format"
- `test_unknown_combination_fallback` - Returns sensible fallback for unmapped combinations

### 3.2 GREEN: Create title mapping ✅

**File**: [`app/graphql/pos/validations/constants.py`](../../app/graphql/pos/validations/constants.py)

Added `ISSUE_TITLE_MAPPING` dict and `get_issue_title()` helper function.

### 3.3 RED: Write failing tests for service ✅

**File**: [`tests/graphql/pos/validations/services/test_file_validation_issue_service.py`](../../tests/graphql/pos/validations/services/test_file_validation_issue_service.py)

**Test scenarios**:
- `test_get_pending_issues_grouped_by_type` - Returns issues from all pending files, grouped by ValidationType
- `test_get_pending_issues_excludes_sent_files` - Issues from sent files not included
- `test_get_pending_issues_includes_file_info` - Each issue has file_id and file_name
- `test_get_issue_by_id` - Returns single issue with row data
- `test_get_issue_by_id_not_found` - Returns None for non-existent issue

### 3.4 GREEN: Create FileValidationIssueService ✅

**File**: [`app/graphql/pos/validations/services/file_validation_issue_service.py`](../../app/graphql/pos/validations/services/file_validation_issue_service.py)

Methods:
- `get_pending_issues_grouped() -> dict[ValidationType, list[FileValidationIssue]]`
- `get_by_id(issue_id: UUID) -> FileValidationIssue | None`

### 3.5 GREEN: Update repository ✅

**File**: [`app/graphql/pos/validations/repositories/file_validation_issue_repository.py`](../../app/graphql/pos/validations/repositories/file_validation_issue_repository.py)

Added methods:
- `get_by_id(issue_id: UUID) -> FileValidationIssue | None`
- `get_by_pending_files() -> list[FileValidationIssue]`

### 3.6 VERIFY: Run `task all` ✅

All checks passed. 9 tests pass (4 title mapping + 5 service).

---

## Phase 4: GraphQL Layer

_Create GraphQL types and queries._

### 4.1 RED: Write failing tests for GraphQL queries ✅

**File**: [`tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py`](../../tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py)

**Test scenarios** (added 4 tests for new types):
- `test_lite_response_includes_file_info` - Lite response includes fileId/fileName
- `test_lite_response_derives_title` - Lite response derives title
- `test_detail_response_includes_row_data` - Detail response includes row_data
- `test_grouped_response_structure` - Grouped response has correct structure

### 4.2 GREEN: Create response types ✅

**File**: [`app/graphql/pos/validations/strawberry/file_validation_issue_types.py`](../../app/graphql/pos/validations/strawberry/file_validation_issue_types.py)

New types:
- `FileValidationIssueLiteResponse` - For list view (id, rowNumber, title, columnName, validationType, fileId, fileName)
- `FileValidationIssueResponse` - For detail view (includes title, fileId, fileName, rowData)
- `ValidationIssueGroupResponse` - Group container (items, count)
- `FileValidationIssuesResponse` - Root response (standardValidation, validationWarning)

### 4.3 GREEN: Create queries ✅

**File**: [`app/graphql/pos/validations/queries/file_validation_issue_queries.py`](../../app/graphql/pos/validations/queries/file_validation_issue_queries.py)

Added queries:
- `fileValidationIssues` → `FileValidationIssuesResponse`
- `fileValidationIssue(id: ID!)` → `FileValidationIssueResponse | None`

### 4.4 GREEN: Register with DI container ✅

Service auto-discovered via `class_suffix="service"` pattern in DI discovery.

### 4.5 VERIFY: Run `task all` ✅

All checks passed. Schema exported with new queries.

### 4.6 REFACTOR: Remove deprecated query and consolidate types ✅

**Rationale**: The old `fileValidationIssues(exchangeFileId)` query (from plan 2026-01-23-01) is no longer needed. The UI uses the global list query and `fileValidationIssue(id)` for details. Also, issues will be deleted when files are sent (future plan), so "pending" prefix is unnecessary.

**Changes**:
- Remove `fileValidationIssues(exchangeFileId)` query ✅
- Delete old `FileValidationIssueResponse` (without file info and rowData) ✅
- Rename `FileValidationIssueDetailResponse` → `FileValidationIssueResponse` (keeping all fields: title, file_id, file_name, row_data) ✅
- Rename `pendingFileValidationIssues` → `fileValidationIssues` ✅
- Rename `PendingFileValidationIssuesResponse` → `FileValidationIssuesResponse` ✅
- Update tests accordingly ✅

---

## Phase 5: Verification

_Manual testing in GraphQL playground._

### 5.1 Test grouped query ✅

- Upload multiple files that generate validation issues
- Query `fileValidationIssues` and verify:
  - Issues are grouped by ValidationType
  - Each issue includes `fileId` and `fileName`
  - Titles are derived correctly

**Testing Results (2026-01-30):**

Uploaded test file `test_validation_v4.csv` with intentional validation errors:
- Row 3: Missing `selling_branch_zip_code`
- Row 4: Invalid ZIP code format (`invalid-zip`)
- Row 5: Future date (`2026-12-31`)
- Row 6: Non-numeric quantity (`abc`)

Query result:
```json
{
  "fileValidationIssues": {
    "standardValidation": {
      "count": 3,
      "items": [
        {"title": "Invalid ZIP code format", "fileName": "test_validation_v4.csv", "rowNumber": 4},
        {"title": "Future date not allowed", "fileName": "test_validation_v4.csv", "rowNumber": 5},
        {"title": "Invalid numeric value", "fileName": "test_validation_v4.csv", "rowNumber": 6}
      ]
    },
    "validationWarning": {"count": 0, "items": []}
  }
}
```

### 5.2 Test detail query ✅

- Query `fileValidationIssue(id)` for a specific issue
- Verify `rowData` contains the original row values

**Result:**
```json
{
  "fileValidationIssue": {
    "id": "23752996-60dd-4459-953b-75eadb209a59",
    "title": "Invalid ZIP code format",
    "rowNumber": 4,
    "columnName": "selling_branch_zip_code",
    "validationType": "STANDARD_VALIDATION",
    "message": "Invalid ZIP code format for 'selling_branch_zip_code': invalid-zip",
    "fileId": "ae36bad9-922e-4889-bdfe-8f2aab3c5e0c",
    "fileName": "test_validation_v4.csv",
    "rowData": "{\"transaction_date\":\"2026-01-25\",\"extended_net_price\":\"89.97\",...}"
  }
}
```

**Note**: Testing required creating an org-specific field map for the user's organization (`b6a0893a-871d-4a05-96fe-bb803fb05fbb`). The validation service uses `file.org_id` (uploader's org) to find the field map, not the target organization.

---

## Changes During Testing

_Issues discovered and fixed during testing/review. Prefixes: BF = bugfix, CH = behavior change._

### BF-1: Fix migration branch conflict ✅

**Problem**: Migration `20260127_create_geography_tables.py` had incorrect `down_revision` pointing to `20260123_001` instead of `20260126_001`, causing migration chain to be broken.

**File**: [`alembic/versions/20260127_create_geography_tables.py`](../../alembic/versions/20260127_create_geography_tables.py)

**Fix**: Updated `down_revision` from `"20260123_001"` to `"20260126_001"` to correctly chain after the validation status migration.

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 3 days |
| Phases | 5 |
| Files Modified | 27 |
| Tests Added | 10 |