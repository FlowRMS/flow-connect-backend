# Sent Exchange Files History Query

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1471](https://linear.app/flow-labs/issue/FLO-1471/history-send-data-query)
- **Created**: 2026-02-02 08:59 -03
- **Approved**: 2026-02-02 11:29 -03
- **Finished**: 2026-02-02 18:35 -03
- **PR**: [#28](https://github.com/FlowRMS/flow-py-connect/pull/28)
- **Commit Prefix**: Sent Exchange Files History

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: GraphQL Types](#phase-1-graphql-types)
- [Phase 2: Repository & Service](#phase-2-repository--service)
- [Phase 3: GraphQL Query](#phase-3-graphql-query)
- [Phase 4: Verification](#phase-4-verification)
- [Results](#results)

---

## Overview

Implement a new GraphQL query `sentExchangeFiles` to retrieve the history of files that have been sent (status = "SENT"). The query returns files grouped by **reporting period** and **target organization**.

### Requirements

1. **Query Name**: `sentExchangeFiles`
2. **Filter**: Only files with status = "SENT"
3. **Grouping**: Nested structure - Period → Organizations → Files
4. **Optional Filters**:
   - `period` (String) - Filter by reporting_period
   - `organizations` (list[UUID]) - Filter by target organizations (connected_org_id)
   - `is_pos` (Boolean) - Filter by is_pos flag
   - `is_pot` (Boolean) - Filter by is_pot flag

---

## Design Decisions

### DD-1: Grouped Response Structure

**Decision**: Use nested grouping pattern (Period → Organization → Files) based on existing `OrganizationAliasGroupResponse`.

```graphql
type SentExchangeFilesByPeriodResponse {
  reportingPeriod: String!
  organizations: [SentExchangeFilesByOrgResponse!]!
}

type SentExchangeFilesByOrgResponse {
  connectedOrgId: ID!
  connectedOrgName: String!
  files: [ExchangeFileResponse!]!
  count: Int!
}

# Query
sentExchangeFiles(
  period: String
  organizations: [ID!]
  isPos: Boolean
  isPot: Boolean
): [SentExchangeFilesByPeriodResponse!]!
```

- Users typically view history by period first ("what did I send in Q1?")
- Then drill into organizations within that period
- Reuses existing `ExchangeFileResponse` type for file details

---

## Critical Files

| File | Status | Description |
|------|--------|-------------|
| `app/graphql/pos/data_exchange/strawberry/exchange_file_types.py` | ✅ | Add grouped response types |
| `app/graphql/pos/data_exchange/repositories/exchange_file_repository.py` | ✅ | Add list_sent_files method |
| `app/graphql/pos/data_exchange/services/exchange_file_service.py` | ✅ | Add service method for sent files |
| `app/graphql/pos/data_exchange/queries/exchange_file_queries.py` | ✅ | Add sentExchangeFiles query |
| `tests/graphql/pos/data_exchange/test_sent_exchange_files.py` | ✅ | Query tests |

---

## Phase 1: GraphQL Types ✅

_Add new response types for the grouped response structure._

### 1.1 GREEN: Add response types ✅

**File**: `app/graphql/pos/data_exchange/strawberry/exchange_file_types.py`

New types:
- `SentExchangeFilesByOrgResponse` - Group by organization (connectedOrgId, connectedOrgName, files, count)
- `SentExchangeFilesByPeriodResponse` - Group by period (reportingPeriod, organizations)

### 1.2 VERIFY: Run `task all` ✅

---

## Phase 2: Repository & Service ✅

_Add repository method and service to query SENT files with filters and grouping._

### 2.1 RED: Write failing tests for repository and service ✅

**File**: `tests/graphql/pos/data_exchange/test_sent_exchange_files.py`

**Test scenarios**:
- `test_list_sent_files_returns_only_sent_status` - Excludes PENDING files
- `test_list_sent_files_filters_by_period` - Period filter works
- `test_list_sent_files_filters_by_organizations` - Organizations filter works
- `test_list_sent_files_filters_by_is_pos` - isPos filter works
- `test_list_sent_files_filters_by_is_pot` - isPot filter works
- `test_get_sent_files_grouped_by_period` - Groups files by reporting_period
- `test_get_sent_files_grouped_by_organization` - Within period, groups by target org
- `test_get_sent_files_includes_org_name` - Each org group includes connectedOrgName

### 2.2 GREEN: Implement repository method ✅

**File**: `app/graphql/pos/data_exchange/repositories/exchange_file_repository.py`

New methods:
- `list_sent_files(period, organizations, is_pos, is_pot)` - Query SENT files with optional filters, eager load target_organizations
- `get_org_names_by_ids(org_ids)` - Fetch organization names from orgs database

### 2.3 GREEN: Implement service method ✅

**File**: `app/graphql/pos/data_exchange/services/exchange_file_service.py`

New dataclasses:
- `SentFilesByOrg` - Group by organization (connected_org_id, connected_org_name, files, count)
- `SentFilesByPeriod` - Group by period (reporting_period, organizations)

New method:
- `get_sent_files_grouped(filters)` - Orchestrates query and groups results by period → organization

### 2.4 REFACTOR: Clean up implementation ✅

### 2.5 VERIFY: Run `task all` ✅

---

## Phase 3: GraphQL Query ✅

_Add the sentExchangeFiles query resolver._

### 3.1 GREEN: Implement query resolver ✅

**File**: `app/graphql/pos/data_exchange/queries/exchange_file_queries.py`

New query:
- `sent_exchange_files(period, organizations, is_pos, is_pot)` → `list[SentExchangeFilesByPeriodResponse]`

### 3.2 VERIFY: Run `task all` ✅

---

## Phase 4: Verification ✅

_Manual testing in GraphQL playground._

### 4.1 Test sentExchangeFiles query ✅

- ✅ Query without filters returns all SENT files grouped by period → organization
- ✅ Query with `period` filter returns only matching period
- ✅ Query with `organizations` filter returns only matching orgs
- ✅ Query with `isPos: true` returns only POS files
- ✅ Query with `isPot: true` returns only POT files
- ✅ Query structure verified (connectedOrgName, count fields present)

Note: Empty results expected - no SENT files in test database. Logic verified by unit tests in Phase 2.

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~9.5h |
| Phases | 4 |
| Files Modified | 16 |
| Tests Added | 7 |
