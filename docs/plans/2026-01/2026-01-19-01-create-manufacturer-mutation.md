# Create Manufacturer Mutation

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1072](https://linear.app/flow-labs/issue/FLO-1072/flowpos-create-new-organization)
- **Created**: 2026-01-19 09:47 -03
- **Approved**: 2026-01-19 10:29 -03
- **Finished**: 2026-01-20 14:05 -03
- **PR**: [#9](https://github.com/FlowRMS/flow-py-connect/pull/9)
- **Commit Prefix**: Create Manufacturer

---

## Table of Contents

- [Overview](#overview)
- [Critical Files](#critical-files)
- [Phase 1: Input Types & Validation](#phase-1-input-types--validation)
- [Phase 2: Manufacturer Creation Service](#phase-2-manufacturer-creation-service)
- [Phase 3: GraphQL Mutation](#phase-3-graphql-mutation)
- [Phase 4: Verification](#phase-4-verification)

---

## Overview

Create a new GraphQL mutation `createManufacturer` that creates a pending organization via the FlowConnect API.

**Mutation Signature:**
```graphql
createManufacturer(input: ManufacturerInput!): OrganizationLiteResponse!
```

**ManufacturerInput:**
- `name: String!` - Organization name
- `domain: String!` - Organization domain
- `contact: PosContactInput` - Optional contact for pending invitation

**PosContactInput:**
- `email: String!`

**Business Logic:**
1. Validate organization doesn't exist in remote DB (by domain)
2. Create organization via FlowConnect API (`POST /profiles/orgs`) with status "pending"
3. If contact provided, invite user via `POST /people/invite-to-org` with `{org_id, email}`
4. Return the created organization

---

## Critical Files

| File | Action | Status |
|------|--------|--------|
| [`app/graphql/organizations/strawberry/manufacturer_inputs.py`](../../app/graphql/organizations/strawberry/manufacturer_inputs.py) | Create | ✅ |
| [`app/graphql/organizations/services/manufacturer_creation_service.py`](../../app/graphql/organizations/services/manufacturer_creation_service.py) | Create | ✅ |
| [`app/graphql/organizations/mutations/manufacturer_mutations.py`](../../app/graphql/organizations/mutations/manufacturer_mutations.py) | Create | ✅ |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | Modify | ✅ |
| [`tests/graphql/organizations/services/test_manufacturer_creation_service.py`](../../tests/graphql/organizations/services/test_manufacturer_creation_service.py) | Create | ✅ |
| [`tests/graphql/organizations/mutations/test_manufacturer_mutations.py`](../../tests/graphql/organizations/mutations/test_manufacturer_mutations.py) | Create | ✅ |

---

## Phase 1: Input Types & Validation
*Define GraphQL input types for the mutation*

### 1.1 GREEN: Create input types ✅
**File**: [`app/graphql/organizations/strawberry/manufacturer_inputs.py`](../../app/graphql/organizations/strawberry/manufacturer_inputs.py)

Input types:
- `PosContactInput`: `email` (required string)
- `ManufacturerInput`: `name`, `domain` (required), `contact` (optional `PosContactInput`)

### 1.2 VERIFY: Run `task all` ✅

---

## Phase 2: Manufacturer Creation Service
*Implement business logic for creating manufacturers*

### 2.1 RED: Write failing tests for manufacturer creation service ✅
**File**: [`tests/graphql/organizations/services/test_manufacturer_creation_service.py`](../../tests/graphql/organizations/services/test_manufacturer_creation_service.py)

**Test scenarios:**
- `test_create_manufacturer_success` - Creates org via API when domain doesn't exist
- `test_create_manufacturer_with_contact_creates_invitation` - Creates pending invitation when contact provided
- `test_create_manufacturer_raises_error_when_domain_exists` - Raises `ConflictError` if domain already exists
- `test_create_manufacturer_raises_error_on_api_failure` - Raises `RemoteApiError` on API failure
- `test_create_manufacturer_raises_error_on_invitation_failure` - Raises `RemoteApiError` if invitation creation fails

### 2.2 GREEN: Implement manufacturer creation service ✅
**File**: [`app/graphql/organizations/services/manufacturer_creation_service.py`](../../app/graphql/organizations/services/manufacturer_creation_service.py)

Class: `ManufacturerCreationService`

Dependencies:
- `FlowConnectApiClient` - For remote API calls
- `ManufacturerRepository` - For domain validation (remote DB)

Methods:
- `async def create(input: ManufacturerInput) -> RemoteOrg` - Main creation logic

Logic flow:
1. Query remote DB to check if domain exists
2. Call `POST /profiles/orgs` with body: `{name, domain, org_type: "manufacturer", status: "pending"}`
3. If contact provided, call `POST /people/invite-to-org` with body: `{org_id, email}`
4. Fetch and return the created org from remote DB

### 2.3 REFACTOR: Clean up, ensure type safety ✅

### 2.4 VERIFY: Run `task all` ✅

---

## Phase 3: GraphQL Mutation
*Wire up the mutation to the schema*

### 3.1 RED: Write failing tests for mutation ✅
**File**: [`tests/graphql/organizations/mutations/test_manufacturer_mutations.py`](../../tests/graphql/organizations/mutations/test_manufacturer_mutations.py)

**Test scenarios:**
- `test_maps_org_fields_correctly` - OrganizationLiteResponse maps fields correctly
- `test_counts_active_memberships` - Counts only active memberships
- `test_input_structure` - ManufacturerInput has correct structure
- `test_input_with_contact` - ManufacturerInput accepts optional contact

### 3.2 GREEN: Implement mutation ✅
**File**: [`app/graphql/organizations/mutations/manufacturer_mutations.py`](../../app/graphql/organizations/mutations/manufacturer_mutations.py)

Class: `ManufacturerMutations`

Method:
```python
@strawberry.mutation()
@inject
async def create_manufacturer(
    self,
    input: ManufacturerInput,
    service: Injected[ManufacturerCreationService],
) -> OrganizationLiteResponse
```

### 3.3 GREEN: Register mutation in schema ✅
**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

Add `ManufacturerMutations` to the `Mutation` class inheritance.

### 3.4 VERIFY: Run `task all` ✅

---

## Phase 4: Verification ✅
*Manual testing in GraphQL Playground*

### 4.1 Test mutation in GraphQL Playground ✅

Test cases:
1. Create manufacturer without contact ✅
2. Create manufacturer with contact ✅
3. Attempt to create with existing domain (expect error) ✅
4. Test with invalid input (expect validation error) ✅

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~1 day |
| Phases | 4 |
| Files Modified | 16 |
| Tests Added | 9 |
