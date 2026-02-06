# POS Dashboard Glance Query

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1583](https://linear.app/flow-labs/issue/FLO-1583/pos-dashboard-glance-query)
- **Created**: 2026-02-05 09:47 -03
- **Approved**: 2026-02-05 11:36 -03
- **Finished**: 2026-02-05 13:15 -03
- **PR**: [#36](https://github.com/FlowRMS/flow-py-connect/pull/36)
- **Commit Prefix**: POS Dashboard Glance Query

---

## Table of Contents

- [Overview](#overview)
- [Data Source Analysis](#data-source-analysis)
- [Design Decisions](#design-decisions)
- [Critical Files](#critical-files)
- [Phase 1: Types Layer](#phase-1-types-layer)
- [Phase 2: Repository Methods](#phase-2-repository-methods)
- [Phase 3: Service Layer](#phase-3-service-layer)
- [Phase 4: GraphQL Query & Schema](#phase-4-graphql-query--schema)
- [Phase 5: Verification](#phase-5-verification)
- [GraphQL API Changes](#graphql-api-changes)
- [Review](#review)
- [Results](#results)

---

## Overview

New GraphQL query `getPosDashboardGlance` that returns aggregated summary data for the POS domain dashboard's "At a glance" section.

**Frontend mockup metrics** (discarding "Next scheduled"):

| Metric | Mockup Example | Description |
|--------|---------------|-------------|
| **Issues** | `2 blocking sends` | Count of individual blocking validation issues across all pending files |
| **Partners** | `2` + `+1 pending` | ACCEPTED connections + PENDING connections count |
| **Messages** | `2 unread` | Unread message count (empty response for now, no messaging system yet) |
| **Last delivery** | `Dec 28` + `1,234 records` | Most recent SENT file's date and its `row_count` |

---

## Data Source Analysis

| Metric | Source Table | Session Type | Existing Infra |
|--------|-------------|-------------|---------------|
| **Issues** | `connect_pos.file_validation_issues` | `TenantSession` | `BLOCKING_VALIDATION_KEYS`, `FileValidationIssueRepository` |
| **Partners** | `subscription.connections` | `AsyncSession` | `ConnectionRepository`, `ConnectionStatus` enum |
| **Messages** | N/A | N/A | Not implemented — hardcoded empty response |
| **Last delivery** | `connect_pos.exchange_files` | `TenantSession` | `ExchangeFileRepository`, `ExchangeFileStatus.SENT` |

**Cross-database precedent**: `ExchangeFileService` already depends on both `TenantSession` and `AsyncSession` repositories. The dashboard service follows the same pattern.

---

## Design Decisions

### DD-1: Nested response types

**Decision**: Use nested types (`DashboardIssuesGlance`, `DashboardPartnersGlance`, etc.) rather than flat fields.

- Maps naturally to the mockup's card-based UI (each card = one nested type)
- More extensible — adding fields to a section doesn't pollute the top-level type
- `lastDelivery` can be `null` when no deliveries exist, which is cleaner as a nullable object
- Frontend can destructure each section independently

### DD-2: Add methods to existing repositories

**Decision**: Add new count/query methods to existing repositories (`FileValidationIssueRepository`, `ConnectionRepository`, `ExchangeFileRepository`) rather than creating dashboard-specific repositories.

- Keeps data access logic close to its domain
- Avoids duplicating model imports and query patterns
- The dashboard service aggregates via DI — same pattern as `ExchangeFileService`

### DD-3: Messages as empty response

**Decision**: Include `messages` field in the response type with hardcoded `unread: 0`. The field exists in the schema but returns zero until the messaging domain is built.

- Frontend can render the section immediately with real structure
- No schema change needed when messaging is implemented — just populate the data

### DD-4: New dashboard subdomain

**Decision**: Create `app/graphql/pos/dashboard/` as a new subdomain.

- This query aggregates across multiple domains (validations, connections, data_exchange)
- Placing it in any existing subdomain would create a misleading ownership
- Follows the existing pattern of one subdomain per concern

---

## Critical Files

| # | File | Action | Status |
|---|------|--------|--------|
| 1 | `app/graphql/pos/dashboard/__init__.py` | Create | ✅ |
| 2 | `app/graphql/pos/dashboard/strawberry/__init__.py` | Create | ✅ |
| 3 | `app/graphql/pos/dashboard/strawberry/dashboard_types.py` | Create | ✅ |
| 4 | `app/graphql/pos/dashboard/services/__init__.py` | Create | ✅ |
| 5 | `app/graphql/pos/dashboard/services/dashboard_glance_service.py` | Create | ✅ |
| 6 | `app/graphql/pos/dashboard/queries/__init__.py` | Create | ✅ |
| 7 | `app/graphql/pos/dashboard/queries/dashboard_queries.py` | Create | ✅ |
| 8 | `app/graphql/pos/validations/repositories/file_validation_issue_repository.py` | Modify | ✅ |
| 9 | `app/graphql/connections/repositories/connection_repository.py` | Modify | ✅ |
| 10 | `app/graphql/pos/data_exchange/repositories/exchange_file_repository.py` | Modify | ✅ |
| 11 | `schema.graphql` | Modify | ✅ |
| 12 | `tests/graphql/pos/dashboard/test_dashboard_types.py` | Create | ✅ |
| 13 | `tests/graphql/pos/dashboard/test_dashboard_glance_service.py` | Create | ✅ |
| 14 | `tests/graphql/pos/dashboard/test_dashboard_queries.py` | Create | ✅ |
| 15 | `tests/graphql/pos/validations/repositories/test_file_validation_issue_repository.py` | Modify | ✅ |
| 16 | `tests/graphql/connections/test_connection_repository.py` | Modify | ✅ |
| 17 | `tests/graphql/pos/data_exchange/test_exchange_file_repository.py` | Modify | ✅ |

---

## Phase 1: Types Layer

_Define Strawberry response types for the dashboard glance query._

### 1.1 RED: Write failing tests for response types ✅

Test scenarios:
- `test_dashboard_issues_glance_construction` — verify field defaults and construction
- `test_dashboard_partners_glance_construction` — connected + pending counts
- `test_dashboard_messages_glance_construction` — unread count defaults to 0
- `test_dashboard_last_delivery_glance_construction` — date + record_count
- `test_pos_dashboard_glance_response_construction` — full response with all nested types
- `test_pos_dashboard_glance_response_with_null_last_delivery` — lastDelivery can be None

### 1.2 GREEN: Implement Strawberry types ✅

**Types to create** in `dashboard_types.py`:

```graphql
type DashboardIssuesGlance {
  blockingSendsCount: Int!
}

type DashboardPartnersGlance {
  connectedCount: Int!
  pendingCount: Int!
}

type DashboardMessagesGlance {
  unreadCount: Int!
}

type DashboardLastDeliveryGlance {
  date: DateTime!
  recordCount: Int!
}

type PosDashboardGlanceResponse {
  issues: DashboardIssuesGlance!
  partners: DashboardPartnersGlance!
  messages: DashboardMessagesGlance!
  lastDelivery: DashboardLastDeliveryGlance
}
```

### 1.3 REFACTOR: Clean up and run `task all` ✅

---

## Phase 2: Repository Methods

_Add count/query methods to existing repositories for the data the dashboard needs._

### 2.1 RED: Write failing tests for new repository methods ✅

Test scenarios for `FileValidationIssueRepository`:
- `test_count_blocking_issues_for_all_pending_files` — returns total count across all pending files
- `test_count_blocking_issues_for_all_pending_files_no_issues` — returns 0 when no blocking issues
- `test_count_blocking_issues_for_all_pending_files_ignores_sent` — only counts issues on PENDING files

Test scenarios for `ConnectionRepository`:
- `test_count_connections_accepted` — counts ACCEPTED connections
- `test_count_connections_pending` — counts PENDING connections
- `test_count_connections_excludes_other_statuses` — ignores DRAFT, DECLINED

Test scenarios for `ExchangeFileRepository`:
- `test_get_last_sent_file` — returns the most recent SENT file
- `test_get_last_sent_file_no_sent_files` — returns None when no files sent
- `test_get_last_sent_file_ignores_pending` — only considers SENT files

### 2.2 GREEN: Implement repository methods ✅

**FileValidationIssueRepository** — new method:
- `count_blocking_issues_for_all_pending_files(org_id: UUID) -> int`
- Joins `file_validation_issues` with `exchange_files` WHERE status=PENDING AND validation_key IN BLOCKING_VALIDATION_KEYS

**ConnectionRepository** — new method:
- `count_by_status(org_id: UUID, status: ConnectionStatus) -> int`
- Counts connections where org is requester OR target, filtered by status

**ExchangeFileRepository** — new method:
- `get_last_sent_file(org_id: UUID) -> ExchangeFile | None`
- Selects most recent SENT file ordered by `created_at DESC LIMIT 1`

### 2.3 REFACTOR: Clean up and run `task all` ✅

---

## Phase 3: Service Layer

_Create the dashboard glance service that aggregates data from multiple repositories._

### 3.1 RED: Write failing tests for DashboardGlanceService ✅

Test scenarios:
- `test_get_glance_returns_all_metrics` — happy path with data for all sections
- `test_get_glance_no_issues` — issues count is 0
- `test_get_glance_no_partners` — both connected and pending are 0
- `test_get_glance_no_deliveries` — lastDelivery is None
- `test_get_glance_messages_always_zero` — messages.unreadCount is always 0

### 3.2 GREEN: Implement DashboardGlanceService ✅

**Constructor dependencies** (via DI):
- `FileValidationIssueRepository` (TenantSession)
- `ConnectionRepository` (AsyncSession)
- `ExchangeFileRepository` (TenantSession)
- `AuthInfo`

**Method**: `get_glance() -> PosDashboardGlanceResponse`
- Calls the three repository methods
- Assembles the response with nested types
- Messages hardcoded to `DashboardMessagesGlance(unread_count=0)`

### 3.3 REFACTOR: Clean up and run `task all` ✅

---

## Phase 4: GraphQL Query & Schema

_Wire the query resolver, update schema.graphql, and register in DI._

### 4.1 RED: Write failing tests for the query resolver ✅

Test scenarios:
- `test_pos_dashboard_glance_query_returns_response` — resolver returns PosDashboardGlanceResponse
- `test_pos_dashboard_glance_query_null_last_delivery` — resolver handles null lastDelivery

### 4.2 GREEN: Implement query and schema ✅

- Create `dashboard_queries.py` with `pos_dashboard_glance` field
- Update `schema.graphql` with new types and query
- Register dashboard module in the POS query root

### 4.3 REFACTOR: Clean up and run `task all` ✅

---

## Phase 5: Verification

_Final verification that all checks pass and manual testing confirms expected behavior._

### 5.1 Run `task all` ✅

Type checks, linting, and all 422 tests pass.

### 5.2 Verify schema.graphql ✅

Schema export matches committed file — up to date.

### 5.3 Review file sizes ✅

All new files under 300 lines. Largest: `test_dashboard_glance_service.py` at 152 lines.

### 5.4 Manual Testing ✅

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Query `posDashboardGlance` with org that has blocking issues on pending files | `issues.blockingSendsCount` returns correct count | ✅ `3` (8 pending files) |
| 2 | Query `posDashboardGlance` with org that has no blocking issues | `issues.blockingSendsCount` returns `0` | N/A (no test org without issues) |
| 3 | Query `posDashboardGlance` with org that has ACCEPTED connections | `partners.connectedCount` returns correct count | ✅ `1` |
| 4 | Query `posDashboardGlance` with org that has PENDING connections | `partners.pendingCount` returns correct count | ✅ `0` (no pending) |
| 5 | Query `posDashboardGlance` with org that has no connections | `partners.connectedCount` and `partners.pendingCount` both return `0` | N/A (test org has 1 connection) |
| 6 | Query `posDashboardGlance` — messages field | `messages.unreadCount` returns `0` (hardcoded) | ✅ `0` |
| 7 | Query `posDashboardGlance` with org that has sent files | `lastDelivery.date` and `lastDelivery.recordCount` match the most recent SENT file | N/A (no sent files) |
| 8 | Query `posDashboardGlance` with org that has no sent files | `lastDelivery` is `null` | ✅ `null` |

---

## GraphQL API Changes

_Non-breaking additions to the GraphQL schema._

| Change | Type | Detail |
|--------|------|--------|
| New query `posDashboardGlance` | ✅ Non-breaking | New query, no existing queries affected |
| New type `PosDashboardGlanceResponse` | ✅ Non-breaking | New type |
| New type `DashboardIssuesGlance` | ✅ Non-breaking | New type |
| New type `DashboardPartnersGlance` | ✅ Non-breaking | New type |
| New type `DashboardMessagesGlance` | ✅ Non-breaking | New type |
| New type `DashboardLastDeliveryGlance` | ✅ Non-breaking | New type |

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns — all queries use indexed columns, simple COUNT/LIMIT 1 |
| 2 | Effects on other features | ✅ No negative effects — new query only, no existing queries modified |
| 3 | Code quality issues | ✅ Clean — follows existing patterns (DI, service aggregation, Strawberry types) |
| 4 | Potential bugs | ✅ None found — null handling for lastDelivery, auth guard for org_id |
| 5 | Commit messages | ✅ Single-line, correct format |
| 6 | No Co-Authored-By | ✅ None found |
| 7 | Breaking changes | ✅ Documented in GraphQL API Changes — all non-breaking additions |
| 8 | Document updates | ✅ TOC updated with Review link |

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~1h 39m |
| Phases | 5 |
| Files Created | 10 |
| Files Modified | 7 |
| Tests Added | 17 |
| Total Tests | 422 |
