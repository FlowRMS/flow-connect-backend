# Hotfix: Fix flowConnectMember Using Wrong Table

- **Status**: 🟦 Complete
- **Related Plan**: [Manufacturer Search Connected Filter](../../plans/2026-01/2026-01-15-manufacturer-search-connected-filter.md)
- **Created**: 2026-02-02 20:05 -03
- **Approved**: 2026-02-02 21:03 -03
- **Finished**: 2026-02-02 21:53 -03
- **PR**: https://github.com/FlowRMS/flow-py-connect/pull/30
- **Commit Prefix**: Flow Connect Member Fix

## Problem

The `connectionSearch` GraphQL query with `flowConnectMember: true` returns incorrect results. Organizations that are Flow Connect members are not being returned correctly.

## Cause

The code uses `RemoteTenant` model which maps to `subscription.tenants`. This is the **wrong table**. Flow Connect membership should be determined by `public.tenant_registry`, not `subscription.tenants`.

## Solution

1. Create a new model `TenantRegistry` that maps to `public.tenant_registry` (id, org_id, status fields)

2. Update `OrganizationSearchRepository.search()` to use `TenantRegistry` instead of `RemoteTenant`:
   - Check `status == 'active'` instead of `is_active == True`
   - Remove `deleted_at` check (not needed)

## Files Changed

| File | Change | Status |
|------|--------|--------|
| `app/graphql/organizations/models/tenant_registry.py` | Create new model for `public.tenant_registry` | ✅ |
| `app/graphql/organizations/models/__init__.py` | Export `TenantRegistry` | ✅ |
| `app/graphql/organizations/repositories/organization_search_repository.py` | Use `TenantRegistry` instead of `RemoteTenant` | ✅ |

_Status: ⬜ = Pending, ✅ = Complete_

## Testing

- ✅ Query `connectionSearch` with `flowConnectMember: true` returns only Flow Connect members
- ✅ Query `connectionSearch` with `flowConnectMember: false` returns only non-members
- ✅ Query without filter returns correct `flowConnectMember` values for each org

## Results

| Metric | Value |
|--------|-------|
| Duration | 50 min |
| Files Modified | 3 |
| Tests Added | 0 |
