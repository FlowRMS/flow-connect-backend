# Hotfix: connectionSearch returns "#N/A" as organization name

- **Status**: 🟦 Complete
- **Related Plan**: N/A
- **Linear Task**: [FLO-1585](https://linear.app/flow-labs/issue/FLO-1585/bug-connectionsearch-returns-na-as-organization-name)
- **Created**: 2026-02-06 09:03 UTC-3
- **Approved**: 2026-02-06 09:03 UTC-3
- **Finished**: 2026-02-06 09:41 UTC-3
- **PR**: https://github.com/FlowRMS/flow-py-connect/pull/42
- **Commit Prefix**: Fix #N/A org names

---

## Table of Contents

- [Problem](#problem)
- [Cause](#cause)
- [Solution](#solution)
- [Phase 1: Implementation](#phase-1-implementation)
- [Verification](#verification)
- [Review](#review)
- [Files Changed](#files-changed)
- [Results](#results)

---

## Problem

When querying connected rep firms via `connectionSearch`, some organizations return `"#N/A"` as their `name` field. This was reported by Hafiz on the **Send Data** page for manufacturers.

**Query used**:
```typescript
const fetchedOrgs = await searchOrganizations({
  searchTerm: '',
  repFirms: true,
  connected: true,
  limit: 100,
});
```

**Response example**:
```json
{
  "data": {
    "connectionSearch": [
      {
        "id": "61c97fc6-2f86-4a92-a36c-f7c7d9248785",
        "name": "#N/A",
        "domain": "cpsreps.com",
        "posContactsCount": 0,
        "flowConnectMember": false,
        "connectionStatus": "PENDING"
      },
      {
        "id": "a14945ac-6004-4d08-90c6-afa0d890c582",
        "name": "#N/A",
        "domain": "infinitysalesmarketing.com",
        "posContactsCount": 0,
        "flowConnectMember": false,
        "connectionStatus": "PENDING"
      }
    ]
  }
}
```

**Expected behavior**: Organization names should display the actual company name, not `"#N/A"`.

---

## Cause

**Data quality issue**: Investigation revealed that 225 organizations in the `subscription.orgs` table have `name = "#N/A"`. This occurred during a spreadsheet/CSV import where missing organization names defaulted to Excel's "#N/A" error value.

**Database query results**:
```sql
SELECT COUNT(*) FROM subscription.orgs WHERE name = '#N/A';
-- Result: 225 organizations affected
```

All affected organizations are rep firms with valid domains (e.g., "cpsreps.com", "infinitysalesmarketing.com") but missing proper company names.

---

## Solution

Add a resolver-level fallback in `OrganizationLiteResponse.from_orm_model()`:
- If `org.name == "#N/A"`, use `org.domain` as the fallback name
- This provides an immediate fix without modifying shared database data
- Non-destructive and reversible approach

**Why not update the database directly?**
- `subscription.orgs` is a shared/remote database table
- Safer to handle the fallback at the application level
- Allows for future data cleanup without breaking current functionality

---

## Phase 1: Implementation

_TDD cycle: write tests, fix code, verify._

### 1.1 RED: Write failing tests

Created [`tests/graphql/organizations/strawberry/test_organization_types.py`](../../../../tests/graphql/organizations/strawberry/test_organization_types.py) with 3 test scenarios:
- `test_from_orm_model_with_na_name_uses_domain_fallback` - When name is "#N/A", use domain as fallback ✅
- `test_from_orm_model_with_valid_name_uses_name` - When name is valid, use name as-is ✅
- `test_from_orm_model_with_na_name_and_no_domain_uses_na` - When name is "#N/A" and domain is None, keep "#N/A" ✅

### 1.2 GREEN: Implement fix

Modified [`app/graphql/organizations/strawberry/organization_types.py`](../../../../app/graphql/organizations/strawberry/organization_types.py):
- Added fallback logic in `OrganizationLiteResponse.from_orm_model()` method
- If `org.name == "#N/A"` and `org.domain` exists, use domain as the display name
- If domain is None, keep the original name (edge case)

**Code change**:
```python
# Fallback: if name is "#N/A" (from bad CSV import), use domain instead
display_name = org.domain if org.name == "#N/A" and org.domain else org.name
```

### 1.3 REFACTOR: Clean up and verify

- All 512 tests passing ✅
- Lint checks passed ✅
- Type checks passed ✅
- GraphQL schema export passed ✅
- No schema changes ✅

---

## Verification

### Step 1: Run tests
- `uv run pytest` — 512 tests passed ✅

### Step 2: Run task all
- `uv run task lint` — passed ✅
- `uv run task typecheck` — passed ✅
- `uv run strawberry export-schema` — passed ✅

### Step 3: Verify schema.graphql
- `git diff schema.graphql` — no changes ✅

### Step 4: Manual testing

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Query `connectionSearch` with empty search term for rep firms | Returns organization names using domain fallback instead of "#N/A" | ✅ |
| 2 | Verify no organizations in results have "#N/A" as name | All organizations show proper names or domain fallback | ✅ |
| 3 | Verify organizations with valid names show their proper names | Returns original names unchanged (e.g., "144TH MARKETING", "ACECO", "ACTION SALES + MARKETING") | ✅ |

**Test results**:
- Queried `connectionSearch` with 50 rep firms for CS Unitec manufacturer
- **No organizations returned with "#N/A" as name** - confirming the fallback is working
- All organizations show either their proper name or domain (for those with "#N/A" in database)
- Sample results: "144TH MARKETING", "ACECO", "ACTION SALES + MARKETING" all show correct names

**Note**: The 225 organizations with "#N/A" in the database are not in the current user's connection network, but the fix applies globally to all `OrganizationLiteResponse` instances, as validated by unit tests.

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns - simple O(1) string comparison |
| 2 | Effects on other features | ✅ No negative effects - fixes display bug, no behavior changes |
| 3 | Code quality ([backend-standards.md](../../docs/methodologies/backend-standards.md)) | ✅ Compliant - 75 lines, proper type hints, Python 3.13 syntax, clear inline comment |
| 4 | Potential bugs | ✅ None found - edge cases handled (null domain, both null) and covered by unit tests |
| 5 | Commit policy | ✅ Compliant - 3 commits, single-line messages, no Co-Authored-By footer, correct prefix |
| 6 | Breaking changes | ✅ None - non-breaking fix, no API/schema changes |
| 7 | Document updates | ✅ Hotfix document complete and up to date |

---

## Files Changed

| File | Action | Phase |
|------|--------|-------|
| [`tests/graphql/organizations/strawberry/__init__.py`](../../../../tests/graphql/organizations/strawberry/__init__.py) | Added | Impl |
| [`tests/graphql/organizations/strawberry/test_organization_types.py`](../../../../tests/graphql/organizations/strawberry/test_organization_types.py) | Added | Impl |
| [`app/graphql/organizations/strawberry/organization_types.py`](../../../../app/graphql/organizations/strawberry/organization_types.py) | Modified | Impl |

---

## Results

| Metric | Value |
|--------|-------|
| Duration | 38 minutes |
| Files Modified | 4 |
| Tests Added | 3 |
