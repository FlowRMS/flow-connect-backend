# File Validation Execution

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1272](https://linear.app/flow-labs/issue/FLO-1272/flowpos-send-data-validation-no-ai-powered-validation)
- **Created**: 2026-01-23 19:04 -03
- **Approved**: 2026-01-23 19:29 -03
- **Finished**: 2026-01-27 09:27 -03
- **PR**: [#21](https://github.com/FlowRMS/flow-py-connect/pull/21)
- **Commit Prefix**: File Validation Execution

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Database Schema](#database-schema)
- [Critical Files](#critical-files)
- [Phase 1: Database Schema](#phase-1-database-schema)
- [Phase 2: File Reader Service](#phase-2-file-reader-service)
- [Phase 3: Validation Pipeline](#phase-3-validation-pipeline)
- [Phase 4: Validation Execution Service](#phase-4-validation-execution-service)
- [Phase 5: Background Task Integration](#phase-5-background-task-integration)
- [Phase 6: GraphQL Layer](#phase-6-graphql-layer)
- [Phase 7: Verification](#phase-7-verification)
- [Results](#results)

---

## Overview

Implement automatic file validation for uploaded exchange files. When a file is uploaded, a background task runs all applicable validations against each row and stores any issues found.

**Key Features:**
- Validate CSV, XLS, XLSX files against 11 validation rules (7 standard + 4 warnings)
- Use Pipeline pattern for extensible validation execution
- Store validation issues per row/column for future editing capability
- Block file submission if standard validation errors exist
- Run validations automatically in background after upload

**Scope:**
- Standard Validation (7 rules) - blocking
- Validation Warning (4 rules) - non-blocking
- AI-Powered Validation - out of scope

---

## Design Decisions

### 1. Pipeline Pattern (Chain of Responsibility)

Each validator is independent and processes the file data sequentially. This allows:
- Easy addition/removal of validators
- Clear separation of concerns
- Individual validator testing

**Reference**: Gang of Four - Chain of Responsibility pattern, adapted for data validation pipelines.

### 2. Validation Status (Separate Field)

Add `validation_status` field to ExchangeFile separate from workflow `status`:
- `NOT_VALIDATED` - just uploaded, awaiting validation
- `VALIDATING` - validation in progress
- `VALID` - all validations passed (or only warnings)
- `INVALID` - has blocking validation errors

This separates validation state from workflow state (PENDING/SENT).

### 3. Background Processing

Use `asyncio.create_task()` to trigger validation immediately after upload without blocking the response. Simple approach for initial implementation.

### 4. Fail-Fast for Blocking Validations

If any STANDARD_VALIDATION fails, stop processing and don't run VALIDATION_WARNING rules. This prevents noise from non-blocking warnings when fundamental issues exist.

### 5. Field Map Integration

Validations use the organization's field map to:
- Map customer column names to standard fields
- Determine field types (date, decimal, integer, text)
- Identify required fields

---

## Database Schema

### ExchangeFile (Modified)

Add new field:

| Column | Type | Constraints |
|--------|------|-------------|
| `validation_status` | `String(20)` | NOT NULL, DEFAULT `not_validated`, indexed |

### FileValidationIssue (New)

| | **`file_validation_issues`** | |
|-----|------|-------|
| **Column** | **Type** | **Constraints** |
| `id` | `UUID` | PK |
| `exchange_file_id` | `UUID` | FK → `exchange_files`, NOT NULL, indexed |
| `row_number` | `Integer` | NOT NULL |
| `column_name` | `String(100)` | NULL (some validations are row-level) |
| `validation_key` | `String(50)` | NOT NULL |
| `message` | `String(500)` | NOT NULL |
| `created_at` | `DateTime` | NOT NULL |
| | **Indexes** | |
| | `ix_file_validation_issues_exchange_file_id` | `exchange_file_id` |
| | **Constraints** | |
| | `fk_file_validation_issues_exchange_file` | CASCADE DELETE |

---

## Critical Files

| File | Status | Description |
|------|--------|-------------|
| [`app/graphql/pos/data_exchange/models/enums.py`](../../app/graphql/pos/data_exchange/models/enums.py) | ✅ | Add ValidationStatus enum |
| [`app/graphql/pos/data_exchange/models/exchange_file.py`](../../app/graphql/pos/data_exchange/models/exchange_file.py) | ✅ | Add validation_status field |
| [`app/graphql/pos/validations/models/file_validation_issue.py`](../../app/graphql/pos/validations/models/file_validation_issue.py) | ✅ | New model |
| [`alembic/versions/20260126_add_validation_status_and_issues.py`](../../alembic/versions/20260126_add_validation_status_and_issues.py) | ✅ | Migration |
| [`app/graphql/pos/validations/services/file_reader_service.py`](../../app/graphql/pos/validations/services/file_reader_service.py) | ✅ | Read CSV/XLS/XLSX files |
| [`app/graphql/pos/validations/services/validators/base.py`](../../app/graphql/pos/validations/services/validators/base.py) | ✅ | Base validator interface |
| `app/graphql/pos/validations/services/validators/*.py` | ✅ | Individual validators (11 total) |
| [`app/graphql/pos/validations/services/validation_pipeline.py`](../../app/graphql/pos/validations/services/validation_pipeline.py) | ✅ | Pipeline orchestration |
| [`app/graphql/pos/validations/services/validation_execution_service.py`](../../app/graphql/pos/validations/services/validation_execution_service.py) | ✅ | Main execution service |
| [`app/graphql/pos/validations/repositories/file_validation_issue_repository.py`](../../app/graphql/pos/validations/repositories/file_validation_issue_repository.py) | ✅ | Repository |
| [`app/graphql/pos/data_exchange/services/exchange_file_service.py`](../../app/graphql/pos/data_exchange/services/exchange_file_service.py) | ✅ | Trigger background validation |
| [`app/graphql/pos/validations/strawberry/file_validation_issue_types.py`](../../app/graphql/pos/validations/strawberry/file_validation_issue_types.py) | ✅ | GraphQL types |
| [`app/graphql/pos/validations/queries/file_validation_issue_queries.py`](../../app/graphql/pos/validations/queries/file_validation_issue_queries.py) | ✅ | GraphQL queries |

---

## Phase 1: Database Schema

Add validation_status to ExchangeFile and create FileValidationIssue model.

### 1.1 GREEN: Create ValidationStatus enum ✅

**File**: [`app/graphql/pos/data_exchange/models/enums.py`](../../app/graphql/pos/data_exchange/models/enums.py)

Add `ValidationStatus` enum with values:
- `NOT_VALIDATED = "not_validated"`
- `VALIDATING = "validating"`
- `VALID = "valid"`
- `INVALID = "invalid"`

### 1.2 GREEN: Add validation_status to ExchangeFile ✅

**File**: [`app/graphql/pos/data_exchange/models/exchange_file.py`](../../app/graphql/pos/data_exchange/models/exchange_file.py)

Add `validation_status` field with default `NOT_VALIDATED`, indexed.

### 1.3 GREEN: Create FileValidationIssue model ✅

**File**: [`app/graphql/pos/validations/models/file_validation_issue.py`](../../app/graphql/pos/validations/models/file_validation_issue.py)

Create model with fields: `exchange_file_id`, `row_number`, `column_name`, `validation_key`, `message`, `created_at`.

### 1.4 GREEN: Create migration ✅

**File**: [`alembic/versions/20260126_add_validation_status_and_issues.py`](../../alembic/versions/20260126_add_validation_status_and_issues.py)

Migration to:
- Add `validation_status` column to `exchange_files`
- Create `file_validation_issues` table

### 1.5 VERIFY: Run `task all` ✅

---

## Phase 2: File Reader Service

Create a service to read file contents from S3 and parse into rows.

### 2.1 RED: Write failing tests for file reader ✅

**File**: [`tests/graphql/pos/validations/services/test_file_reader_service.py`](../../tests/graphql/pos/validations/services/test_file_reader_service.py)

**Test scenarios**:
- `test_read_csv_file_returns_rows` - Parse CSV content into list of dicts
- `test_read_xls_file_returns_rows` - Parse XLS content into list of dicts
- `test_read_xlsx_file_returns_rows` - Parse XLSX content into list of dicts
- `test_read_file_with_header_mapping` - Map customer columns to standard fields using field map
- `test_read_file_invalid_format_raises_error` - Unsupported file type raises exception

### 2.2 GREEN: Implement FileReaderService ✅

**File**: [`app/graphql/pos/validations/services/file_reader_service.py`](../../app/graphql/pos/validations/services/file_reader_service.py)

Service that:
- Downloads file from S3 using S3Service
- Parses based on file_type (CSV, XLS, XLSX)
- Maps columns using organization's field map
- Returns list of `FileRow` dataclass with row_number and data dict

### 2.3 VERIFY: Run `task all` ✅

---

## Phase 3: Validation Pipeline

Create the validation pipeline with individual validators.

### 3.1 RED: Write failing tests for validators ✅

**File**: [`tests/graphql/pos/validations/services/validators/test_validators.py`](../../tests/graphql/pos/validations/services/validators/test_validators.py)

**Test scenarios for each validator**:

**RequiredFieldValidator**:
- `test_required_field_missing_returns_issue` - Missing required field creates issue
- `test_required_field_present_passes` - Present field passes
- `test_required_field_empty_string_returns_issue` - Empty string treated as missing

**DateFormatValidator**:
- `test_valid_date_mm_dd_yyyy_passes` - MM/DD/YYYY format passes
- `test_valid_date_yyyy_mm_dd_passes` - YYYY-MM-DD format passes
- `test_invalid_date_format_returns_issue` - Invalid format creates issue

**NumericFieldValidator**:
- `test_valid_integer_passes` - Integer field passes
- `test_valid_decimal_passes` - Decimal field passes
- `test_non_numeric_value_returns_issue` - Non-numeric creates issue

**ZipCodeValidator**:
- `test_valid_5_digit_zip_passes` - 5-digit ZIP passes
- `test_valid_9_digit_zip_passes` - 9-digit ZIP (with hyphen) passes
- `test_invalid_zip_returns_issue` - Invalid ZIP creates issue

**PriceCalculationValidator**:
- `test_correct_calculation_passes` - qty × unit_cost = extended_price
- `test_incorrect_calculation_returns_issue` - Mismatch creates issue
- `test_missing_fields_skips_validation` - Skip if fields missing

**FutureDateValidator**:
- `test_past_date_passes` - Past date passes
- `test_today_passes` - Today's date passes
- `test_future_date_returns_issue` - Future date creates issue

**LineLevelDataValidator**:
- Defer implementation details - complex heuristic validation

**CatalogNumberFormatValidator** (Warning):
- `test_catalog_with_prefix_returns_warning` - Detected prefix creates warning

**LotOrderDetectionValidator** (Warning):
- `test_lot_order_type_returns_warning` - LST/DIRECT_SHIP/etc creates warning

**ShipFromLocationValidator** (Warning):
- `test_different_ship_from_returns_warning` - Different location creates warning

**LostFlagValidator** (Warning):
- `test_lost_flag_present_returns_warning` - Lost flag creates warning

### 3.2 GREEN: Create base validator interface ✅

**File**: [`app/graphql/pos/validations/services/validators/base.py`](../../app/graphql/pos/validations/services/validators/base.py)

Abstract base class `BaseValidator`:
- `validation_key: str` - identifier for this validation
- `validation_type: ValidationType` - STANDARD_VALIDATION or VALIDATION_WARNING
- `validate(row: FileRow, field_map: FieldMap) -> list[ValidationIssue]`

`ValidationIssue` dataclass with: `row_number`, `column_name`, `validation_key`, `message`

### 3.3 GREEN: Implement standard validators (blocking) ✅

**Files**: `app/graphql/pos/validations/services/validators/`
- [`required_field_validator.py`](../../app/graphql/pos/validations/services/validators/required_field_validator.py)
- [`date_format_validator.py`](../../app/graphql/pos/validations/services/validators/date_format_validator.py)
- [`numeric_field_validator.py`](../../app/graphql/pos/validations/services/validators/numeric_field_validator.py)
- [`zip_code_validator.py`](../../app/graphql/pos/validations/services/validators/zip_code_validator.py)
- [`price_calculation_validator.py`](../../app/graphql/pos/validations/services/validators/price_calculation_validator.py)
- [`future_date_validator.py`](../../app/graphql/pos/validations/services/validators/future_date_validator.py)
- [`line_level_data_validator.py`](../../app/graphql/pos/validations/services/validators/line_level_data_validator.py)

### 3.4 GREEN: Implement warning validators (non-blocking) ✅

**Files**: `app/graphql/pos/validations/services/validators/`
- [`catalog_number_format_validator.py`](../../app/graphql/pos/validations/services/validators/catalog_number_format_validator.py)
- [`lot_order_detection_validator.py`](../../app/graphql/pos/validations/services/validators/lot_order_detection_validator.py)
- [`ship_from_location_validator.py`](../../app/graphql/pos/validations/services/validators/ship_from_location_validator.py)
- [`lost_flag_validator.py`](../../app/graphql/pos/validations/services/validators/lost_flag_validator.py)

### 3.5 VERIFY: Run `task all` ✅

---

## Phase 4: Validation Execution Service

Create the main service that orchestrates validation execution.

### 4.1 RED: Write failing tests for ValidationPipeline ✅

**File**: [`tests/graphql/pos/validations/services/test_validation_pipeline.py`](../../tests/graphql/pos/validations/services/test_validation_pipeline.py)

**Test scenarios**:
- `test_pipeline_runs_all_validators` - All validators execute
- `test_pipeline_stops_on_blocking_errors` - If standard validation fails, warnings skip
- `test_pipeline_continues_with_warnings_only` - No blocking errors, warnings run
- `test_pipeline_collects_all_issues` - Issues from all validators collected

### 4.2 GREEN: Implement ValidationPipeline ✅

**File**: [`app/graphql/pos/validations/services/validation_pipeline.py`](../../app/graphql/pos/validations/services/validation_pipeline.py)

Pipeline that:
- Registers validators in order (blocking first, then warnings)
- Processes each row through validators
- Stops after blocking validators if any issues found
- Returns all collected issues

### 4.3 RED: Write failing tests for FileValidationIssueRepository ✅

**File**: [`tests/graphql/pos/validations/repositories/test_file_validation_issue_repository.py`](../../tests/graphql/pos/validations/repositories/test_file_validation_issue_repository.py)

**Test scenarios**:
- `test_create_issues_bulk` - Create multiple issues for a file
- `test_get_issues_by_file_id` - Get all issues for a file
- `test_delete_issues_by_file_id` - Clear issues before re-validation
- `test_count_blocking_issues` - Count only STANDARD_VALIDATION issues

### 4.4 GREEN: Implement FileValidationIssueRepository ✅

**File**: [`app/graphql/pos/validations/repositories/file_validation_issue_repository.py`](../../app/graphql/pos/validations/repositories/file_validation_issue_repository.py)

Repository with bulk create, query by file, delete by file, count methods.

### 4.5 RED: Write failing tests for ValidationExecutionService ✅

**File**: [`tests/graphql/pos/validations/services/test_validation_execution_service.py`](../../tests/graphql/pos/validations/services/test_validation_execution_service.py)

**Test scenarios**:
- `test_validate_file_updates_status_to_validating` - Status changes to VALIDATING
- `test_validate_file_with_errors_sets_invalid` - Blocking errors set INVALID
- `test_validate_file_success_sets_valid` - No blocking errors set VALID
- `test_validate_file_stores_issues` - Issues persisted to database
- `test_validate_file_clears_previous_issues` - Re-validation clears old issues

### 4.6 GREEN: Implement ValidationExecutionService ✅

**File**: [`app/graphql/pos/validations/services/validation_execution_service.py`](../../app/graphql/pos/validations/services/validation_execution_service.py)

Service that:
1. Updates file status to VALIDATING
2. Reads file content using FileReaderService
3. Gets organization's field map
4. Runs ValidationPipeline
5. Stores issues using repository
6. Updates file status to VALID or INVALID

### 4.7 VERIFY: Run `task all` ✅

---

## Phase 5: Background Task Integration

Trigger validation automatically after file upload.

### 5.1 RED: Write failing tests for background trigger ✅

**File**: [`tests/graphql/pos/data_exchange/test_exchange_file_service.py`](../../tests/graphql/pos/data_exchange/test_exchange_file_service.py)

**Test scenarios**:
- `test_upload_file_triggers_validation_task` - Validation starts after upload
- `test_upload_file_returns_immediately` - Upload doesn't wait for validation

### 5.2 GREEN: Integrate background task in upload ✅

**File**: [`app/graphql/pos/data_exchange/services/exchange_file_service.py`](../../app/graphql/pos/data_exchange/services/exchange_file_service.py)

Modify `upload_file` method to:
- After successful upload, trigger `asyncio.create_task()` for validation
- Return immediately with file in NOT_VALIDATED status

### 5.3 GREEN: Create background task function ✅

**File**: [`app/graphql/pos/validations/services/validation_task.py`](../../app/graphql/pos/validations/services/validation_task.py)

Async function that:
- Creates new database session (background tasks need own session)
- Instantiates ValidationExecutionService
- Runs validation
- Handles errors gracefully (log but don't crash)

### 5.4 VERIFY: Run `task all` ✅

---

## Phase 6: GraphQL Layer

Expose validation status and issues via GraphQL.

### 6.1 GREEN: Update ExchangeFile response types ✅

**File**: [`app/graphql/pos/data_exchange/strawberry/exchange_file_types.py`](../../app/graphql/pos/data_exchange/strawberry/exchange_file_types.py)

Add `validation_status` field to `ExchangeFileLiteResponse` and `ExchangeFileResponse`.

### 6.2 RED: Write failing tests for validation issues query ✅

**File**: [`tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py`](../../tests/graphql/pos/validations/queries/test_file_validation_issue_queries.py)

**Test scenarios**:
- `test_response_structure` - Response has correct structure
- `test_from_model_maps_fields` - Maps fields correctly
- `test_from_model_handles_none_column_name` - Handles row-level validations
- `test_validation_type_derived_from_key_blocking` - Blocking keys return STANDARD_VALIDATION
- `test_validation_type_derived_from_key_warning` - Warning keys return VALIDATION_WARNING

### 6.3 GREEN: Create FileValidationIssue response types ✅

**File**: [`app/graphql/pos/validations/strawberry/file_validation_issue_types.py`](../../app/graphql/pos/validations/strawberry/file_validation_issue_types.py)

Create `FileValidationIssueResponse` with: `id`, `row_number`, `column_name`, `validation_key`, `message`, `validation_type` (derived from key).

### 6.4 GREEN: Create validation issues query ✅

**File**: [`app/graphql/pos/validations/queries/file_validation_issue_queries.py`](../../app/graphql/pos/validations/queries/file_validation_issue_queries.py)

Query `file_validation_issues(exchange_file_id: ID!) -> list[FileValidationIssueResponse]`

### 6.5 GREEN: Register query in schema ✅

**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

Add FileValidationIssueQueries to schema.

### 6.6 VERIFY: Run `task all` ✅

---

## Phase 7: Verification

Manual testing and integration verification.

### 7.1 Unit Test Coverage ✅

All 121 validation-related tests pass:

**Validation Flow Tests:**
- `test_upload_file_triggers_validation_task` - Upload triggers background validation ✅
- `test_upload_file_returns_immediately` - Upload doesn't block on validation ✅
- `test_validate_file_updates_status_to_validating` - Status update to VALIDATING ✅
- `test_validate_file_with_errors_sets_invalid` - INVALID status on blocking errors ✅
- `test_validate_file_success_sets_valid` - VALID status on success ✅
- `test_validate_file_stores_issues` - Issues persisted to database ✅
- `test_validate_file_clears_previous_issues` - Re-validation clears old issues ✅
- `test_pipeline_runs_all_validators` - Full pipeline execution ✅
- `test_pipeline_stops_on_blocking_errors` - Fail-fast on standard validation ✅

**GraphQL API Tests:**
- `pendingExchangeFiles` query returns `validationStatus` field ✅
- `fileValidationIssues` query returns validation issues with derived `validationType` ✅

### 7.2 DI Integration Fixes ✅

Fixed import-time environment variable checks that prevented provider registration:
- Added `dotenv.load_dotenv()` in `service_providers.py`, `repository_providers.py`, `orgs_db_provider.py`
- Used absolute paths via `Path(__file__)` for env files
- Fixed circular import in `validation_task.py` by deferring `create_container` import

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 4 days |
| Phases | 7 |
| Files Modified | 51 |
| Tests Added | 47 |
