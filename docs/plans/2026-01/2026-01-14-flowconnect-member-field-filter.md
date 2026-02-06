# Plan: Add FlowConnect Member Field and Filter

- **Status**: Complete
- **Created**: 2026-01-14
- **Completed**: 2026-01-14

## Summary

Add a `flowConnectMember: Boolean!` field to `OrganizationLiteResponse` and a `flowConnectMember: Boolean | None` filter to `manufacturerSearch` query. An organization is a FlowConnect member if it has an active record in `subscription.tenants`.

## Filter Behavior

- `flowConnectMember: null` (default) - Return all results
- `flowConnectMember: true` - Return only FlowConnect members
- `flowConnectMember: false` - Return only non-members

## Implementation Approach: EXISTS Subquery

Use SQLAlchemy EXISTS subquery for efficient single-query implementation:

```sql
SELECT
    orgs.*,
    EXISTS (
        SELECT 1 FROM subscription.tenants t
        WHERE t.org_id = orgs.id
          AND t.is_active = true
          AND t.deleted_at IS NULL
    ) AS flow_connect_member
FROM subscription.orgs
WHERE ...
```

**Benefits:**
- No N+1 queries - single SQL statement
- Efficient EXISTS short-circuits after first match
- Filter applied at database level

---

## Files to Create/Modify

### Step 1: Create RemoteTenant Model (NEW)
**File**: `app/graphql/organizations/models/remote_tenant.py`

```python
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.graphql.organizations.models.remote_org import OrgsBase


class RemoteTenant(OrgsBase):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    org_id: Mapped[uuid.UUID] = mapped_column()
    is_active: Mapped[bool | None] = mapped_column()
    deleted_at: Mapped[datetime | None] = mapped_column()
```

### Step 2: Export RemoteTenant
**File**: `app/graphql/organizations/models/__init__.py`

Add import and export for `RemoteTenant`.

### Step 3: Update Repository with EXISTS Subquery
**File**: `app/graphql/organizations/repositories/manufacturer_repository.py`

```python
from sqlalchemy import and_, exists, select
from app.graphql.organizations.models import RemoteTenant

async def search(
    self,
    search_term: str,
    *,
    active: bool = True,
    flow_connect_member: bool | None = None,
    limit: int = 20,
) -> list[tuple[RemoteOrg, bool]]:
    # EXISTS subquery
    tenant_exists = (
        select(RemoteTenant.id)
        .where(
            and_(
                RemoteTenant.org_id == RemoteOrg.id,
                RemoteTenant.is_active.is_(True),
                RemoteTenant.deleted_at.is_(None),
            )
        )
        .exists()
    )

    stmt = (
        select(RemoteOrg, tenant_exists.label("flow_connect_member"))
        .options(selectinload(RemoteOrg.memberships))
        .where(...)
    )

    # Apply filter
    if flow_connect_member is True:
        stmt = stmt.where(tenant_exists)
    elif flow_connect_member is False:
        stmt = stmt.where(~tenant_exists)

    result = await self.session.execute(stmt)
    return [(row.RemoteOrg, row.flow_connect_member) for row in result.all()]
```

### Step 4: Update Service
**File**: `app/graphql/organizations/services/manufacturer_service.py`

Pass through `flow_connect_member` parameter.

### Step 5: Add Field to OrganizationLiteResponse
**File**: `app/graphql/organizations/strawberry/organization_types.py`

```python
@strawberry.type
class OrganizationLiteResponse:
    # ... existing fields ...
    flow_connect_member: bool

    @staticmethod
    def from_orm_model(
        org: RemoteOrg,
        *,
        flow_connect_member: bool = False,
    ) -> "OrganizationLiteResponse":
        return OrganizationLiteResponse(
            id=strawberry.ID(str(org.id)),
            name=org.name,
            domain=org.website,
            members=len([m for m in org.memberships if m.deleted_at is None]),
            pos_contacts_count=0,
            pos_contacts=[],
            flow_connect_member=flow_connect_member,
        )
```

### Step 6: Add Filter to Query
**File**: `app/graphql/organizations/queries/manufacturer_queries.py`

```python
async def manufacturer_search(
    self,
    search_term: str,
    service: Injected[ManufacturerService],
    active: bool = True,
    flow_connect_member: bool | None = None,
    limit: int = 20,
) -> list[OrganizationLiteResponse]:
    results = await service.search(
        search_term,
        active=active,
        flow_connect_member=flow_connect_member,
        limit=limit,
    )
    return [
        OrganizationLiteResponse.from_orm_model(org, flow_connect_member=is_member)
        for org, is_member in results
    ]
```

---

## GraphQL Schema Changes

**Before:**
```graphql
manufacturerSearch(searchTerm: String!, active: Boolean! = true, limit: Int! = 20): [OrganizationLiteResponse!]!
```

**After:**
```graphql
manufacturerSearch(
    searchTerm: String!
    active: Boolean! = true
    flowConnectMember: Boolean = null
    limit: Int! = 20
): [OrganizationLiteResponse!]!

type OrganizationLiteResponse {
    id: ID!
    name: String!
    domain: String
    members: Int!
    posContactsCount: Int!
    posContacts: [PosContact!]!
    flowConnectMember: Boolean!  # NEW
}
```

---

## Implementation Sequence

- [x] Create `app/graphql/organizations/models/remote_tenant.py`
- [x] Update `app/graphql/organizations/models/__init__.py`
- [x] Update `app/graphql/organizations/repositories/manufacturer_repository.py`
- [x] Update `app/graphql/organizations/services/manufacturer_service.py`
- [x] Update `app/graphql/organizations/strawberry/organization_types.py`
- [x] Update `app/graphql/organizations/queries/manufacturer_queries.py`
- [x] Run `task all`

---

## Verification

1. **Type checks & tests**: Run `task all`
2. **Test field**:
   ```graphql
   query {
     manufacturerSearch(searchTerm: "test") {
       id
       name
       flowConnectMember
     }
   }
   ```
3. **Test filter (members only)**:
   ```graphql
   query {
     manufacturerSearch(searchTerm: "test", flowConnectMember: true) {
       name
       flowConnectMember  # All should be true
     }
   }
   ```
4. **Test filter (non-members only)**:
   ```graphql
   query {
     manufacturerSearch(searchTerm: "test", flowConnectMember: false) {
       name
       flowConnectMember  # All should be false
     }
   }
   ```

---

## Critical Files

| File | Action |
|------|--------|
| `app/graphql/organizations/models/remote_tenant.py` | CREATE |
| `app/graphql/organizations/models/__init__.py` | EDIT |
| `app/graphql/organizations/repositories/manufacturer_repository.py` | EDIT |
| `app/graphql/organizations/services/manufacturer_service.py` | EDIT |
| `app/graphql/organizations/strawberry/organization_types.py` | EDIT |
| `app/graphql/organizations/queries/manufacturer_queries.py` | EDIT |

---

## Notes

### Why EXISTS Subquery vs LEFT JOIN

We chose EXISTS subquery over LEFT JOIN for the following reasons:

1. **EXISTS short-circuits** - Stops scanning after finding the first match, making it efficient for existence checks
2. **Index utilization** - The `idx_tenants_org_id` index on `subscription.tenants(org_id)` makes each lookup O(log n)
3. **LIMIT 20 caps executions** - The subquery runs at most 20 times (once per result row), not 20,000 times
4. **Cleaner filter logic** - `WHERE EXISTS` / `WHERE NOT EXISTS` is more readable than join conditions

LEFT JOIN would also work (since `org_id` has UNIQUE constraint), but EXISTS is more semantically correct for "does a record exist?" queries.

### Design Decisions

- **No default value for `flow_connect_member` parameter** - The `from_orm_model` method requires explicit `flow_connect_member` value to prevent silent `False` defaults for future callers
- **Tri-state filter** - `null` (all), `true` (members only), `false` (non-members only) - matches the pattern of the existing `active` filter
- **Minimal RemoteTenant model** - Only includes fields needed for the EXISTS subquery (`id`, `org_id`, `is_active`, `deleted_at`)