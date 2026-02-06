# FLO-1310 - Flow Connect Backend Staging Deployment Test

**Date:** 2026-02-06
**Environment:** Staging
**DNS:** `https://staging.flowconnectbackend.flowrms.com`
**Render URL:** `https://flow-connect-backend-staging.onrender.com`

## 1. Health Check

```bash
curl -s https://staging.flowconnectbackend.flowrms.com/api/health
```

**Response:**
```json
{"status": "ok"}
```

**Result:** PASS

## 2. Unauthenticated Request

```bash
curl -s -X POST https://staging.flowconnectbackend.flowrms.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

**Response:**
```json
{"data": null, "errors": [{"message": "Unauthorized. Access token is required"}]}
```

**Result:** PASS - Correctly rejects unauthenticated requests.

## 3. Invalid Token Request

```bash
curl -s -X POST https://staging.flowconnectbackend.flowrms.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token" \
  -d '{"query": "{ __typename }"}'
```

**Response:**
```json
{"data": null, "errors": [{"message": "Unauthorized. Not enough segments"}]}
```

**Result:** PASS - Correctly rejects invalid JWT tokens.

## 4. Authenticated Request (WorkOS JWT)

Authentication was performed using WorkOS User Management API (`password` grant type) with organization selection (`urn:workos:oauth:grant-type:organization-selection`).

```bash
curl -s -X POST https://staging.flowconnectbackend.flowrms.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <WORKOS_ACCESS_TOKEN>" \
  -d '{"query": "{ __typename }"}'
```

**Response:**
```json
{"data": {"__typename": "Query"}}
```

**Result:** PASS - Authenticated request succeeds.

## 5. Schema Introspection

```bash
curl -s -X POST https://staging.flowconnectbackend.flowrms.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <WORKOS_ACCESS_TOKEN>" \
  -d '{"query": "{ __schema { queryType { fields { name } } mutationType { fields { name } } } }"}'
```

**Response - Available Queries (18):**

| # | Query Field |
|---|------------|
| 1 | connectionSearch |
| 2 | userOrganization |
| 3 | organizationPreference |
| 4 | organizationPreferencesByApplication |
| 5 | organizationPreferences |
| 6 | posDashboardGlance |
| 7 | fieldMap |
| 8 | organizationAliases |
| 9 | fileValidationIssues |
| 10 | fileValidationIssue |
| 11 | filteredFileValidationIssues |
| 12 | prefixPatterns |
| 13 | validationRules |
| 14 | pendingExchangeFiles |
| 15 | pendingExchangeFilesStats |
| 16 | sentExchangeFiles |
| 17 | receivedExchangeFiles |
| 18 | health |

**Response - Available Mutations (18):**

| # | Mutation Field |
|---|---------------|
| 1 | createConnection |
| 2 | inviteConnection |
| 3 | updateConnectionTerritories |
| 4 | uploadAgreement |
| 5 | deleteAgreement |
| 6 | createConnectOrganization |
| 7 | updateOrganizationPreference |
| 8 | saveFieldMap |
| 9 | createOrganizationAlias |
| 10 | deleteOrganizationAlias |
| 11 | bulkSpreadsheetCreateOrganizationAliases |
| 12 | createPrefixPattern |
| 13 | deletePrefixPattern |
| 14 | uploadExchangeFiles |
| 15 | deleteExchangeFile |
| 16 | sendPendingExchangeFiles |
| 17 | downloadReceivedExchangeFile |
| 18 | ping |

**Result:** PASS - Full schema available with all 18 queries and 18 mutations.

## Summary

| Test | Status |
|------|--------|
| Health check | PASS |
| Unauthenticated rejection | PASS |
| Invalid token rejection | PASS |
| Authenticated access | PASS |
| Schema introspection | PASS |

All tests passed. The Flow Connect Backend is fully operational on staging with WorkOS JWT authentication and tenant resolution working correctly.
