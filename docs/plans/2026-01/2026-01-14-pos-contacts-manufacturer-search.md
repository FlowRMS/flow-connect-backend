# Plan: Add POS Contacts to Manufacturer Search Response

- **Status**: ✅ Complete
- **Created**: 2026-01-14 10:00
- **Finished**: 2026-01-14 16:45

## Table of Contents

- [Summary](#summary)
- [Critical Files](#critical-files)
- [Phase 1: Database Models ✅](#phase-1-database-models-)
- [Phase 2: POS Contact Repository ✅](#phase-2-pos-contact-repository-)
- [Phase 3: Service Layer ✅](#phase-3-service-layer-)
- [Phase 4: GraphQL Layer ✅](#phase-4-graphql-layer-)
- [Phase 5: Final Verification ✅](#phase-5-final-verification-)
- [Verification](#verification)

---

## Summary

Add actual POS contact data to the `manufacturerSearch` response. Currently, `pos_contacts_count` is hardcoded to 0 and `pos_contacts` is hardcoded to an empty list. This plan implements the full query to fetch real POS contacts from the `subscription` schema.

## Requirements

1. `PosContact` type should have: `id`, `name`, `email`
2. Maximum 5 contacts per organization in `pos_contacts` list
3. `pos_contacts_count` should show the total count (can be > 5)
4. A POS contact = user with "flow-pos" app role AND membership in the organization

## Database Tables (Remote - subscription schema)

- `ar_app_roles` - find "flow-pos" role by role_key
- `ar_user_app_roles` - link users to roles
- `org_memberships` - link users to organizations
- `users` - get contact details (id, email, first_name, last_name)

## Query Logic

```sql
SELECT DISTINCT u.id, u.email, u.first_name, u.last_name
FROM subscription.users u
JOIN subscription.org_memberships om ON om.user_id = u.id
JOIN subscription.ar_user_app_roles uar ON uar.user_id = u.id
JOIN subscription.ar_app_roles ar ON ar.id = uar.app_role_id
WHERE om.org_id = :org_id
  AND om.deleted_at IS NULL
  AND ar.role_key = 'flow-pos';
```

> **Note**: The `name` field in the GraphQL response is computed as `first_name + " " + last_name`.

## Architecture: Two-Step Query

Since `manufacturerSearch` returns at most 20 organizations, we use:
1. First query: Get organizations (existing)
2. Second query: Batch fetch POS contacts for all returned org IDs

This avoids N+1 queries by batching the POS contact lookup.

---

## Critical Files

| File | Action |
|------|--------|
| [`app/graphql/organizations/models/remote_user.py`](../../app/graphql/organizations/models/remote_user.py) | CREATE ✅ |
| [`app/graphql/organizations/models/remote_app_role.py`](../../app/graphql/organizations/models/remote_app_role.py) | CREATE ✅ |
| [`app/graphql/organizations/models/__init__.py`](../../app/graphql/organizations/models/__init__.py) | MODIFY ✅ |
| [`app/graphql/organizations/repositories/pos_contact_repository.py`](../../app/graphql/organizations/repositories/pos_contact_repository.py) | CREATE ✅ |
| [`app/graphql/organizations/repositories/__init__.py`](../../app/graphql/organizations/repositories/__init__.py) | MODIFY ✅ |
| [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py) | MODIFY ✅ |
| [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py) | MODIFY ✅ |
| [`app/graphql/organizations/queries/manufacturer_queries.py`](../../app/graphql/organizations/queries/manufacturer_queries.py) | MODIFY ✅ |

---

## Phase 1: Database Models ✅

Create SQLAlchemy models to map remote tables in the `subscription` schema.

### 1.1 GREEN: Create RemoteUser model ✅

**File**: [`app/graphql/organizations/models/remote_user.py`](../../app/graphql/organizations/models/remote_user.py)

- Map to `subscription.users` table
- Fields: `id`, `email`, `first_name`, `last_name`, `created_at`, `updated_at`, `deleted_at`
- Extend `OrgsBase`

### 1.2 GREEN: Create RemoteAppRole models ✅

**File**: [`app/graphql/organizations/models/remote_app_role.py`](../../app/graphql/organizations/models/remote_app_role.py)

- `RemoteAppRole`: Map to `subscription.ar_app_roles`
  - Fields: `id`, `role_key`, `display_name`, `description`, `created_at`, `updated_at`
- `RemoteUserAppRole`: Map to `subscription.ar_user_app_roles`
  - Fields: `id`, `user_id`, `app_role_id`, `created_by`, `created_at`
  - Relationship to `RemoteAppRole`

### 1.3 GREEN: Update models __init__.py ✅

**File**: [`app/graphql/organizations/models/__init__.py`](../../app/graphql/organizations/models/__init__.py)

Export `RemoteUser`, `RemoteAppRole`, `RemoteUserAppRole`.

### 1.4 VERIFY: Run `task all` ✅

---

## Phase 2: POS Contact Repository ✅

Create repository to batch-fetch POS contacts for multiple organizations.

### 2.1 RED: Write failing tests for PosContactRepository ✅

**File**: [`tests/graphql/organizations/test_pos_contact_repository.py`](../../tests/graphql/organizations/test_pos_contact_repository.py)

**Test scenarios:**
- `test_empty_list_returns_empty_dict` - Returns `{}` when no org_ids provided
- `test_returns_contacts_grouped_by_org` - Groups contacts correctly by org_id
- `test_limits_to_5_per_org` - Returns max 5 contacts but `total_count` reflects actual count

### 2.2 GREEN: Create PosContactRepository ✅

**File**: [`app/graphql/organizations/repositories/pos_contact_repository.py`](../../app/graphql/organizations/repositories/pos_contact_repository.py)

**Data structures:**
- `PosContactData` dataclass: `id`, `name`, `email`
- `OrgPosContacts` dataclass: `contacts` (list), `total_count` (int)

**Method**: `get_pos_contacts_for_orgs(org_ids: list[uuid.UUID]) -> dict[uuid.UUID, OrgPosContacts]`
- Return empty dict if no org_ids
- Subquery: find users with "flow-pos" role
- Main query: join org_memberships with users, filter by org_ids and flow-pos role
- Group results by org_id
- Limit to 5 contacts per org, but preserve total_count

### 2.3 GREEN: Update repositories __init__.py ✅

**File**: [`app/graphql/organizations/repositories/__init__.py`](../../app/graphql/organizations/repositories/__init__.py)

Export `PosContactRepository`.

### 2.4 VERIFY: Run `task all` ✅

---

## Phase 3: Service Layer ✅

Update ManufacturerService to integrate POS contacts using two-step query architecture.

### 3.1 RED: Write failing tests for ManufacturerService ✅

**File**: [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py)

**Test scenarios:**
- `test_search_returns_empty_list_when_no_results` - Returns `[]` when no orgs found
- `test_search_includes_pos_contacts` - Results include POS contacts for each org
- `test_search_handles_org_without_pos_contacts` - Orgs without contacts get empty list

### 3.2 GREEN: Update ManufacturerService ✅

**File**: [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py)

**Changes:**
- Add `ManufacturerSearchResult` dataclass: `org`, `flow_connect_member`, `pos_contacts`
- Inject `PosContactRepository` in constructor
- Update `search()` method:
  1. Get organizations (existing query)
  2. Batch fetch POS contacts for all org IDs
  3. Return `list[ManufacturerSearchResult]` combining org data with POS contacts

### 3.3 GREEN: Update exports ✅

- [`services/__init__.py`](../../app/graphql/organizations/services/__init__.py): Export `ManufacturerSearchResult`
- [`organizations/__init__.py`](../../app/graphql/organizations/__init__.py): Export `PosContactRepository`, `ManufacturerSearchResult`

### 3.4 VERIFY: Run tests ✅

> **Note**: `task all` typecheck fails until Phase 4 updates `manufacturer_queries.py`

---

## Phase 4: GraphQL Layer ✅

Update Strawberry types and resolver to expose POS contact data in the API.

### 4.1 GREEN: Update PosContact type ✅

**File**: [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py)

- Add `name: str | None` and `email: str | None` fields
- Add `from_data(data: PosContactData)` static method

### 4.2 GREEN: Update OrganizationLiteResponse ✅

- Update `from_orm_model()` to accept `pos_contacts: OrgPosContacts | None` parameter
- Populate `pos_contacts_count` and `pos_contacts` from the parameter

### 4.3 GREEN: Update manufacturer_queries.py ✅

**File**: [`app/graphql/organizations/queries/manufacturer_queries.py`](../../app/graphql/organizations/queries/manufacturer_queries.py)

- Update resolver to use `ManufacturerSearchResult` attributes
- Pass `pos_contacts` to `from_orm_model()`

### 4.4 VERIFY: Run `task all` ✅

---

## Phase 5: Final Verification ✅

Manual testing to validate the implementation with real data.

### 5.1 Test via GraphQL playground ✅

Verified via curl request to local server.

---

## Verification

### Test Query

```graphql
query TestPosContacts {
  manufacturerSearch(searchTerm: "test") {
    id
    name
    members
    posContactsCount
    posContacts {
      id
      name
      email
    }
    flowConnectMember
  }
}
```

### Expected Behavior

- `posContactsCount` shows total number of POS contacts (can be > 5)
- `posContacts` contains max 5 contacts with id, name, email
- Organizations without POS contacts show `posContactsCount: 0` and `posContacts: []`

---

## GraphQL Schema Changes

**Before:**
```graphql
type PosContact {
    id: ID!
}
```

**After:**
```graphql
type PosContact {
    id: ID!
    name: String
    email: String
}
```
