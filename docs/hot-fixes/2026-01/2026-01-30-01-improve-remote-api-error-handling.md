# Hotfix: Improve Remote API Error Handling

- **Status**: 🟦 Complete
- **Related Plan**: [Create Manufacturer Mutation](../../plans/2026-01/2026-01-19-01-create-manufacturer-mutation.md)
- **Linear Task**: [FLO-1382](https://linear.app/flow-labs/issue/FLO-1382/createorganization-with-contact-issue)
- **Created**: 2026-01-30 12:00 -03
- **Approved**: 2026-01-30 09:38 -03
- **Finished**: 2026-01-30 11:37 -03
- **PR**: [#24](https://github.com/FlowRMS/flow-py-connect/pull/24)
- **Commit Prefix**: Remote API Error Handling

## Problem

When `createOrganization` fails with a 500 error, the client receives:

```json
{"message": "Remote API error: 500"}
```

**Issues:**
1. No context about **which step** failed (creating org vs inviting contact)
2. Remote API's error message is **discarded**

**Actual remote response (lost):**
```json
{"statusCode": 500, "message": "Failed to create organization: duplicate key value violates unique constraint..."}
```

## Cause

In `raise_for_api_status`:
1. Message extraction only happens for 400 errors, not 500
2. No `context` parameter to identify which operation failed

## Solution

1. Add optional `context` parameter to `raise_for_api_status`
2. Extract message from 500 responses (same as 400)
3. Pass context from service calls (`"Creating organization"`, `"Inviting contact"`)

---

## Implementation

### 1. RED: Write failing tests for error handling improvements

**File**: `tests/core/flow_connect_api/test_response_handler.py`

**Test scenarios:**
- `test_extracts_message_from_500_response` - Returns remote message instead of generic "Remote API error: 500"
- `test_includes_context_in_error_message` - Prefixes error with context when provided
- `test_context_with_extracted_message` - Combines context and remote message correctly
- `test_context_parameter_is_optional` - Existing calls without context still work

### 2. GREEN: Implement error handling improvements

**File**: `app/core/flow_connect_api/response_handler.py`

Changes to `raise_for_api_status`:
- Add optional `context: str | None` parameter
- Call `_extract_remote_message` for 500 errors
- Prefix message with context when provided

### 3. GREEN: Pass context from service

**File**: `app/graphql/organizations/services/organization_creation_service.py`

- Pass `context="Creating organization"` for org creation call
- Pass `context="Inviting contact"` for invitation call

### 4. VERIFY: Run `task all`

---

## Files Changed

| File | Change | Status |
|------|--------|--------|
| `tests/core/flow_connect_api/test_response_handler.py` | Add tests for context and 500 message extraction | ✅ |
| `app/core/flow_connect_api/response_handler.py` | Add context parameter, extract message for 500 | ✅ |
| `app/graphql/organizations/services/organization_creation_service.py` | Pass context to `raise_for_api_status` | ✅ |
| `app/graphql/connections/services/connection_request_service.py` | Pass context to `raise_for_api_status` (opportunistic) | ✅ |

_Status: ⬜ = Pending, ✅ = Complete_

### Opportunistic Refactor

Added context to all existing `raise_for_api_status` calls in the codebase for consistent error handling (per [tdd-standards.md](../methodologies/tdd-standards.md#opportunistic-refactor)).

## Results

| Metric | Value |
|--------|-------|
| Duration | ~2 hours |
| Files Modified | 4 |
| Tests Added | 6 |
