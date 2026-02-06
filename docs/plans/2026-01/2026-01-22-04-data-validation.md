# Data Validation

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1205](https://linear.app/flow-labs/issue/FLO-1205/flowpos-data-validation)
- **Created**: 2026-01-22 17:08 -03
- **Approved**: 2026-01-22 19:03 -03
- **Finished**: 2026-01-22 20:07 -03
- **PR**: [#17](https://github.com/FlowRMS/flow-py-connect/pull/17)
- **Commit Prefix**: Data Validation

---

## Table of Contents

- [Overview](#overview)
- [Validation Data](#validation-data)
- [Critical Files](#critical-files)
- [Phase 1: Schema Design](#phase-1-schema-design)
- [Phase 2: GraphQL Query](#phase-2-graphql-query)
- [Phase 3: Verification](#phase-3-verification)
- [Results](#results)

---

## Overview

Create a GraphQL query that returns a static list of data validations. This is foundational work for a future validation system - for now, it's just exposing the list of available validation types to the frontend.

Each validation has:
- **Name**: Display name of the validation
- **Description**: What the validation does
- **Triggers**: Optional list of strings indicating when the validation is triggered (only 2 validations have this)
- **Type**: One of three categories:
  - `STANDARD_VALIDATION` - Basic data validation rules (7 items)
  - `VALIDATION_WARNING` - Non-blocking warnings (4 items)
  - `AI_POWERED_VALIDATION` - AI-assisted validation (5 items)
- **Enabled**: Boolean indicating if the validation is currently active

**GraphQL Query**: `validations` - Returns the complete list of 16 validations

---

## Validation Data

### Standard Validation (7 items)

1. **Line-level transaction data required**
   - Description: All POS/POT data must be submitted at the individual transaction level. Aggregated or summarized data (e.g., monthly totals by product, rolled-up quantities) will be rejected. Each row must represent a single transaction with its own transaction date, quantity, and pricing.
   - Triggers:
     - Multiple transactions combined into a single row
     - Monthly or weekly summary data instead of daily transactions
     - Aggregated quantities across multiple customers or dates
     - Missing individual transaction identifiers (invoice numbers, dates)
   - Enabled: True

2. **Required field validation**
   - Description: All mandatory NEMRA fields must be present and non-empty.
   - Enabled: True

3. **Date format validation**
   - Description: All dates must be valid and in acceptable formats: MM/DD/YYYY, YYYY-MM-DD
   - Enabled: True

4. **Numeric field validation**
   - Description: Quantity, unit cost, and extended price must be valid numbers.
   - Enabled: True

5. **ZIP code validation**
   - Description: Selling branch ZIP and customer ZIP must be valid 5 or 9 digit formats.
   - Enabled: True

6. **Price calculation check**
   - Description: Extended price is calculated against quantity × unit cost.
   - Enabled: True

7. **Future date prevention**
   - Description: Transaction dates cannot be in the future.
   - Enabled: True

### Validation Warnings (4 items)

8. **Catalog/Part number format check**
   - Description: Distributors are encouraged to match manufacturers with the manufacturer's part number in the format provided in their price/product files, without appended prefixes. If hyphens or other characters are included in the manufacturer part number and can be accommodated by your ERP system, they should be included.
   - Triggers:
     - Part numbers with added distributor prefixes or suffixes
     - Part numbers without hyphens present in manufacturer format
     - Truncated part numbers due to ERP field limits
     - Catalog numbers from a cross-reference matching catalog/product lookup
   - Enabled: True

9. **Lot order detection**
   - Description: Orders with a type of LST, DIRECT_SHIP, PROJECT, or SPECIAL are automatically marked for manufacturer review. Per NEMRA guidance, these orders require separate handling for commission calculations.
   - Enabled: True

10. **Ship-from location comparison**
    - Description: When the ship-from location differs from selling branch, order is flagged as potential direct ship.
    - Enabled: True

11. **Include lost flag**
    - Description: Lost orders are included in POS submissions but clearly labeled. They are never auto-excluded or hidden from manufacturers.
    - Enabled: True

### AI-Powered Validation (5 items)

12. **Duplicate detection**
    - Description: AI identifies potential duplicate records based on multiple field matching.
    - Enabled: True

13. **Anomaly detection**
    - Description: Flags unusual quantities, prices, or patterns that may indicate errors.
    - Enabled: True

14. **Catalog number verification**
    - Description: AI validates manufacturer part numbers against known manufacturer SKUs.
    - Enabled: True

15. **Address standardization**
    - Description: Validates and normalizes ZIP codes and location data.
    - Enabled: True

16. **Historical comparison**
    - Description: Compares submissions against historical patterns to catch outliers.
    - Enabled: True

---

## Critical Files

| File | Status | Description |
|------|--------|-------------|
| [`app/graphql/pos/validations/models/enums.py`](../../app/graphql/pos/validations/models/enums.py) | ✅ | Validation type enum |
| [`app/graphql/pos/validations/strawberry/validation_rule_types.py`](../../app/graphql/pos/validations/strawberry/validation_rule_types.py) | ✅ | Response type with static data |
| [`app/graphql/pos/validations/queries/validation_rule_queries.py`](../../app/graphql/pos/validations/queries/validation_rule_queries.py) | ✅ | GraphQL query |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | ✅ | Register query |
| [`tests/graphql/pos/validations/queries/test_validation_rule_queries.py`](../../tests/graphql/pos/validations/queries/test_validation_rule_queries.py) | ✅ | Tests |

---

## Phase 1: Schema Design

Define the validation type enum and response type with the static validation list.

### 1.1 RED: Write failing tests for validation query ✅

**File**: `tests/graphql/pos/validation/test_validation_queries.py`

**Test scenarios**:
- `test_validations_returns_all_validations` - Returns complete list of validations
- `test_validation_has_required_fields` - Each validation has name, description, triggers, type, enabled
- `test_validation_types_are_valid_enum_values` - Type field is one of the three valid enum values

### 1.2 GREEN: Create enum and response type ✅

**File**: `app/graphql/pos/validation/models/enums.py`
- Create `ValidationType` enum with three values: `STANDARD_VALIDATION`, `VALIDATION_WARNING`, `AI_POWERED_VALIDATION`

**File**: `app/graphql/pos/validation/strawberry/validation_types.py`
- Create `ValidationResponse` type with fields: `name`, `description`, `triggers`, `type`, `enabled`
- Define static `VALIDATIONS` list with all validation entries
- Create `get_all()` static method to return all validations

### 1.3 VERIFY: Run `task all` ✅

---

## Phase 2: GraphQL Query

Wire up the GraphQL query to expose the validations.

### 2.1 GREEN: Create query class ✅

**File**: `app/graphql/pos/validation/queries/validation_queries.py`
- Create `ValidationQueries` class with `validations` field
- Return `ValidationResponse.get_all()`

### 2.2 GREEN: Register query in schema ✅

**File**: `app/graphql/schemas/schema.py`
- Import `ValidationQueries`
- Add to `Query` class inheritance

### 2.3 VERIFY: Run `task all` ✅

---

## Phase 3: Verification

Manual testing in GraphQL playground.

### 3.1 Manual Testing ✅

Test the `validations` query:
- Verify all validations are returned
- Verify each validation has correct structure
- Verify enum values are serialized correctly

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~1 hour |
| Phases | 3 |
| Files Modified | 7 |
| Tests Added | 23 |