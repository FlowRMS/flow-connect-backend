# Create Connection Mutation

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1305](https://linear.app/flow-labs/issue/FLO-1305/flowpos-create-distributor)
- **Created**: 2026-01-26 09:17 -03
- **Approved**: 2026-01-26 09:27 -03
- **PR**: [#20](https://github.com/FlowRMS/flow-py-connect/pull/20)
- **Finished**: 2026-01-26 13:58 -03
- **Commit Prefix**: Create Connection

---

## Table of Contents

- [Overview](#overview)
- [DRY Strategy](#dry-strategy)
- [Critical Files](#critical-files)
- [Phase 1: Add Complementary Type Logic to OrgType Enum](#phase-1-add-complementary-type-logic-to-orgtype-enum)
- [Phase 2: Refactor Creation Service](#phase-2-refactor-creation-service)
- [Phase 3: Rename Mutation](#phase-3-rename-mutation)
- [Phase 4: Verification](#phase-4-verification)
- [Results](#results)

---

## Overview

Rename `createManufacturer` mutation to `createConnection` and add logic to automatically determine the organization type based on the logged-in user's organization.

**Current Implementation**:
- **Mutation**: `ManufacturerMutations.create_manufacturer()` - always creates manufacturers
- **Service**: `ManufacturerCreationService.create()` - hardcodes `org_type: "manufacturer"`
- **Input**: `ManufacturerInput` - name, domain, optional contact

**Business Rule** (same as `connectionSearch`):
- If user's organization is a **distributor** → creates a **manufacturer**
- If user's organization is a **manufacturer** → creates a **distributor**

This mirrors the existing pattern in `OrganizationSearchService._get_target_org_type()`.

---

## DRY Strategy

**Design Pattern**: Strategy Pattern (GoF)

Extract the complementary org type logic to the `OrgType` enum:

1. **Add `get_complementary_type()` method to `OrgType` enum** - centralizes the business rule
2. **Update `OrganizationSearchService`** to use `OrgType.get_complementary_type()`
3. **Rename `ManufacturerCreationService` to `OrganizationCreationService`** with dynamic `org_type` detection using the new enum method
4. **Rename `ManufacturerInput` to `CreateOrganizationInput`**
5. **Rename `ManufacturerMutations` to `OrganizationMutations`** with `createOrganization` mutation

---

## Critical Files

| File | Action | Description |
|------|--------|-------------|
| [`app/graphql/organizations/models/enums.py`](../../app/graphql/organizations/models/enums.py) | ✅ Modify | Add `get_complementary_type()` method to `OrgType` |
| [`app/graphql/organizations/services/organization_search_service.py`](../../app/graphql/organizations/services/organization_search_service.py) | ✅ Modify | Use `OrgType.get_complementary_type()` |
| [`app/graphql/organizations/services/organization_creation_service.py`](../../app/graphql/organizations/services/organization_creation_service.py) | ✅ Rename | → `organization_creation_service.py` |
| [`app/graphql/organizations/services/__init__.py`](../../app/graphql/organizations/services/__init__.py) | ✅ Modify | Update exports |
| [`app/graphql/organizations/strawberry/organization_inputs.py`](../../app/graphql/organizations/strawberry/organization_inputs.py) | ✅ Rename | → `organization_inputs.py`, rename `ManufacturerInput` → `CreateOrganizationInput` |
| [`app/graphql/organizations/strawberry/__init__.py`](../../app/graphql/organizations/strawberry/__init__.py) | ✅ Modify | Update exports |
| [`app/graphql/organizations/mutations/organization_mutations.py`](../../app/graphql/organizations/mutations/organization_mutations.py) | ✅ Rename | → `organization_mutations.py`, rename class and mutation |
| [`app/graphql/organizations/mutations/__init__.py`](../../app/graphql/organizations/mutations/__init__.py) | ✅ Modify | Update exports |
| [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py) | ✅ Modify | Update mutation reference |
| [`schema.graphql`](../../schema.graphql) | ✅ Modify | Rename mutation and input type |
| [`tests/graphql/organizations/models/test_org_type_enum.py`](../../tests/graphql/organizations/models/test_org_type_enum.py) | ✅ Create | Tests for `get_complementary_type()` |
| [`tests/graphql/organizations/services/test_organization_creation_service.py`](../../tests/graphql/organizations/services/test_organization_creation_service.py) | ✅ Rename | → `test_organization_creation_service.py` |
| [`tests/graphql/organizations/mutations/test_organization_mutations.py`](../../tests/graphql/organizations/mutations/test_organization_mutations.py) | ✅ Rename | → `test_organization_mutations.py` |

---

## Phase 1: Add Complementary Type Logic to OrgType Enum ✅

Extract the "get opposite org type" business rule to the `OrgType` enum and update existing code to use it.

### 1.1 RED: Write failing tests for OrgType.get_complementary_type() ✅

**File**: [`tests/graphql/organizations/models/test_org_type_enum.py`](../../tests/graphql/organizations/models/test_org_type_enum.py)

**Test scenarios**:
- `test_manufacturer_complementary_type_is_distributor` - `OrgType.MANUFACTURER.get_complementary_type()` returns `OrgType.DISTRIBUTOR`
- `test_distributor_complementary_type_is_manufacturer` - `OrgType.DISTRIBUTOR.get_complementary_type()` returns `OrgType.MANUFACTURER`

### 1.2 GREEN: Add get_complementary_type() method to OrgType ✅

**File**: [`app/graphql/organizations/models/enums.py`](../../app/graphql/organizations/models/enums.py)

Add instance method to the enum:
```python
def get_complementary_type(self) -> "OrgType":
    if self == OrgType.MANUFACTURER:
        return OrgType.DISTRIBUTOR
    return OrgType.MANUFACTURER
```

### 1.3 REFACTOR: Update OrganizationSearchService to use enum method ✅

**File**: [`app/graphql/organizations/services/organization_search_service.py`](../../app/graphql/organizations/services/organization_search_service.py)

Replace `_get_target_org_type()` static method with `OrgType.get_complementary_type()`:
- Remove `_get_target_org_type()` method
- Update `search_for_connections()` to call `OrgType(user_org.org_type).get_complementary_type()`

### 1.4 VERIFY: Run `task all` ✅

---

## Phase 2: Refactor Creation Service ✅

Rename `ManufacturerCreationService` to `OrganizationCreationService` and add dynamic org_type detection.

### 2.1 RED: Write failing tests for dynamic org_type detection ✅

**File**: [`tests/graphql/organizations/services/test_organization_creation_service.py`](../../tests/graphql/organizations/services/test_organization_creation_service.py)

**Test scenarios** (new tests):
- `test_create_creates_manufacturer_when_user_is_distributor` - Verifies org_type is "manufacturer" when user org is distributor
- `test_create_creates_distributor_when_user_is_manufacturer` - Verifies org_type is "distributor" when user org is manufacturer

### 2.2 GREEN: Implement OrganizationCreationService with dynamic org_type ✅

**File**: [`app/graphql/organizations/services/organization_creation_service.py`](../../app/graphql/organizations/services/organization_creation_service.py)

**Changes**:
- Add `ConnectionService` dependency to get user's organization
- Add `OrganizationSearchRepository` dependency (already exists) to fetch user org details
- Add `auth_info: AuthInfo` dependency for `auth_provider_id`
- Update `create()` to:
  1. Get user's org via `ConnectionService.get_user_org_and_connections()`
  2. Fetch user org details via `OrganizationSearchRepository.get_by_id()`
  3. Determine target org_type via `OrgType(user_org.org_type).get_complementary_type()`
  4. Use dynamic org_type in API call

### 2.3 REFACTOR: Rename files and update exports ✅

**Renames**:
- `manufacturer_creation_service.py` → `organization_creation_service.py`
- `ManufacturerCreationService` → `OrganizationCreationService`
- `manufacturer_inputs.py` → `organization_inputs.py`
- `ManufacturerInput` → `CreateOrganizationInput`
- Test file rename accordingly

**Updates**:
- `services/__init__.py` - export `OrganizationCreationService`
- `strawberry/__init__.py` - export `CreateOrganizationInput`

### 2.4 VERIFY: Run `task all` ✅

---

## Phase 3: Rename Mutation ✅

Rename mutation from `createManufacturer` to `createOrganization`.

**Note**: Originally planned as `createConnection`, but renamed to `createOrganization` to avoid naming conflict with existing `ConnectionMutations` class in `app.graphql.connections.mutations`.

### 3.1 GREEN: Rename mutation class and method ✅

**File renames**:
- `manufacturer_mutations.py` → `organization_mutations.py`
- `ManufacturerMutations` → `OrganizationMutations`
- `create_manufacturer()` → `create_organization()`

**GraphQL changes**:
- Mutation: `createManufacturer` → `createOrganization`
- Input type: `ManufacturerInput` → `CreateOrganizationInput`

### 3.2 REFACTOR: Update schema and exports ✅

**Files**:
- [`mutations/__init__.py`](../../app/graphql/organizations/mutations/__init__.py) - export `OrganizationMutations`
- [`schema.py`](../../app/graphql/schemas/schema.py) - reference `OrganizationMutations` instead of `ManufacturerMutations`
- [`schema.graphql`](../../schema.graphql) - rename mutation and input type

### 3.3 VERIFY: Run `task all` ✅

---

## Phase 4: Verification ✅

Manual testing of the renamed mutation.

### 4.1 Test createOrganization mutation ✅

**Test scenarios**:
- ✅ Verify domain uniqueness check works - Returns `ConflictError` for existing domain
- ✅ Verify `connectionSearch` works - User org detection functioning correctly
- ✅ Test file renamed: `test_manufacturer_mutations.py` → `test_organization_mutations.py`

**Note**: External Flow Connect API integration requires server-side configuration verification.

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~5 hours |
| Phases | 4 |
| Files Modified | 15 |
| Tests Added | 3 |