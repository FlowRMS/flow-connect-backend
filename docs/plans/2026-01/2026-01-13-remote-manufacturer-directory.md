# Remote Manufacturer Directory

- **Date**: 2026-01-13
- **Status**: ✅ Complete

## Overview

Implement a read-only manufacturer directory that fetches data from an external PostgreSQL database (`subscription.orgs` table). This is a temporary solution until the data is migrated to the main database.

## Requirements

- **Environment variable**: `ORGS_DB_URL` for the external database connection
- **Search**: Case-insensitive name search (ILIKE)
- **Filtering**: By active status (default: active only)
- **Limit**: Configurable result limit (default: 20)
- **Read-only**: No writes to the external database

## External Database Schema

```sql
CREATE TABLE "subscription".orgs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    org_type "subscription".org_type NOT NULL,  -- 'manufacturer'
    website text NULL,
    status text DEFAULT 'active'::text NULL,
    workos_org_id text NULL,
    member_approval_required bool DEFAULT true NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    deleted_at timestamptz NULL
);

CREATE TABLE "subscription".org_memberships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    org_id uuid NOT NULL,
    user_id uuid NOT NULL,
    "role" text NOT NULL,
    is_admin bool DEFAULT false NULL,
    is_primary bool DEFAULT false NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    deleted_at timestamptz NULL,
    CONSTRAINT org_memberships_pkey PRIMARY KEY (id),
    CONSTRAINT org_memberships_org_id_user_id_key UNIQUE (org_id, user_id),
    CONSTRAINT org_memberships_org_id_fkey FOREIGN KEY (org_id) REFERENCES "subscription".orgs(id) ON DELETE CASCADE
);
CREATE INDEX org_memberships_org_id_idx ON subscription.org_memberships USING btree (org_id);
```

## Architecture Decision

**Dedicated AsyncEngine** (not MultiTenantController) because:
- Single external database (not multi-tenant)
- Read-only access only
- Simpler configuration

## File Structure

```
app/
├── graphql/
│   ├── di/                           # Dependency injection (aioinject)
│   │   ├── __init__.py
│   │   ├── discovery.py              # Auto-discovery functions
│   │   ├── inject.py                 # Strawberry @inject decorator
│   │   ├── repository_providers.py   # Auto-discovered repositories
│   │   └── service_providers.py      # Auto-discovered services
│   └── organizations/
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── remote_org.py         # SQLAlchemy models for remote org
│       ├── repositories/
│       │   ├── __init__.py
│       │   └── manufacturer_repository.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── manufacturer_service.py
│       ├── queries/
│       │   ├── __init__.py
│       │   └── manufacturer_queries.py
│       └── strawberry/
│           ├── __init__.py
│           └── organization_types.py
└── core/
    └── db/
        └── orgs_db_provider.py       # Dedicated engine for orgs DB
```

## Implementation Steps

### Step 1: Update Settings ✅
**File**: `app/core/config/settings.py`

Add optional `orgs_db_url: PostgresDsn | None = None`

### Step 2: Create Orgs Database Provider ✅
**File**: `app/core/db/orgs_db_provider.py`

```python
class OrgsDbEngine:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.session_factory = async_sessionmaker(...)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session
```

Providers:
- `aioinject.Singleton(create_orgs_db_engine)` - engine
- `aioinject.Scoped(create_orgs_session)` - session per request

### Step 3: Create Organization Model ✅
**File**: `app/graphql/organizations/models/remote_org.py`

```python
class OrgType(StrEnum):
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    REP_FIRM = "rep_firm"
    ASSOCIATION = "association"
    ADMIN_ORG = "admin_org"


class OrgStatus(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"


class OrgsBase(DeclarativeBase):
    pass


class RemoteOrg(OrgsBase):
    __tablename__ = "orgs"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID]
    name: Mapped[str]
    org_type: Mapped[OrgType]
    website: Mapped[str | None]  # Exposed as "domain" in GraphQL
    status: Mapped[OrgStatus | None]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None]

    memberships: Mapped[list[RemoteOrgMembership]] = relationship(back_populates="org")


class RemoteOrgMembership(OrgsBase):
    __tablename__ = "org_memberships"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID]
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscription.orgs.id"))
    user_id: Mapped[uuid.UUID]
    role: Mapped[str]
    is_admin: Mapped[bool | None]
    is_primary: Mapped[bool | None]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None]

    org: Mapped[RemoteOrg] = relationship(back_populates="memberships")
```

### Step 4: Create Manufacturer Repository ✅
**File**: `app/graphql/organizations/repositories/manufacturer_repository.py`

```python
class ManufacturerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(
        self,
        search_term: str,
        *,
        active: bool = True,
        limit: int = 20,
    ) -> list[RemoteOrg]:
        """
        Search manufacturers by name (case-insensitive ILIKE).
        Filters: org_type == 'manufacturer', deleted_at IS NULL
        Optionally filters by status == 'active' when active=True.
        """
```

### Step 5: Create Manufacturer Service ✅
**File**: `app/graphql/organizations/services/manufacturer_service.py`

```python
class ManufacturerService:
    def __init__(self, repository: ManufacturerRepository) -> None:
        self.repository = repository

    async def search(
        self,
        search_term: str,
        *,
        active: bool = True,
        limit: int = 20,
    ) -> list[RemoteOrg]:
        return await self.repository.search(
            search_term, active=active, limit=limit
        )
```

### Step 6: Setup DI (Dependency Injection) Module ✅
**Files**:
- `app/graphql/di/__init__.py`
- `app/graphql/di/discovery.py`
- `app/graphql/di/inject.py`
- `app/graphql/di/repository_providers.py`
- `app/graphql/di/service_providers.py`

The `di/` module centralizes all [aioinject](https://github.com/aioinject/aioinject) (dependency injection library) related code:
- `discovery.py`: Auto-discovery functions (`discover_classes`, `discover_types`, `discover_providers`)
- `inject.py`: Custom `@inject` decorator for Strawberry GraphQL
- `*_providers.py`: Auto-discovered providers for repositories and services

### Step 7: Create GraphQL Types ✅
**File**: `app/graphql/organizations/strawberry/organization_types.py`

```python
@strawberry.type
class PosContact:
    id: strawberry.ID


@strawberry.type
class OrganizationLiteResponse:
    id: strawberry.ID
    name: str
    domain: str | None
    members: int
    pos_contacts_count: int  # Placeholder: always 0 for now
    pos_contacts: list[PosContact]  # Placeholder: always empty for now

    @staticmethod
    def from_orm_model(org: RemoteOrg) -> OrganizationLiteResponse:
        return OrganizationLiteResponse(
            id=strawberry.ID(str(org.id)),
            name=org.name,
            domain=org.website,  # Map website -> domain
            members=len([m for m in org.memberships if m.deleted_at is None]),
            pos_contacts_count=0,  # Placeholder
            pos_contacts=[],  # Placeholder
        )
```

### Step 8: Create GraphQL Query Resolver ✅
**File**: `app/graphql/organizations/queries/manufacturer_queries.py`

```python
@strawberry.type
class ManufacturerQueries:
    @strawberry.field()
    @inject
    async def manufacturer_search(
        self,
        search_term: str,
        service: Injected[ManufacturerService],
        active: bool = True,
        limit: int = 20,
    ) -> list[OrganizationLiteResponse]:
        if not os.environ.get("ORGS_DB_URL"):
            return []
        results = await service.search(search_term, active=active, limit=limit)
        return [OrganizationLiteResponse.from_orm_model(org) for org in results]
```

> **Note**: We check `ORGS_DB_URL` at runtime instead of using `Injected[ManufacturerService | None]` because aioinject cannot resolve union types. See [Lessons Learned](#lessons-learned).

### Step 9: Update GraphQL Schema ✅
**File**: `app/graphql/schemas/schema.py`

```python
from app.graphql.organizations.queries import ManufacturerQueries

@strawberry.type
class Query(ManufacturerQueries):
    @strawberry.field
    def health(self) -> str:
        return "ok"
```

### Step 10: Update Providers Registry ✅
**File**: `app/core/providers.py`

Add imports:
- `from app.core.db import orgs_db_provider`
- `from app.graphql.di import repository_providers, service_providers`

Add to modules list.

## GraphQL API

```graphql
type Query {
    manufacturerSearch(
        searchTerm: String!
        active: Boolean! = true
        limit: Int! = 20
    ): [OrganizationLiteResponse!]!
}

type PosContact {
    id: ID!  # Placeholder
}

type OrganizationLiteResponse {
    id: ID!
    name: String!
    domain: String
    members: Int!
    posContactsCount: Int!       # Placeholder: always 0 for now
    posContacts: [PosContact!]!  # Placeholder: always empty for now
}
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| DB Connection | Dedicated `AsyncEngine` | Simpler than MultiTenantController |
| Session Lifecycle | `aioinject.Scoped` | Session per request |
| Optional Feature | `orgs_db_url | None` | Graceful degradation |
| Null Handling | `Service | None` | Feature disabled when env var not set |
| Connection Pool | `NullPool` | Avoid exhaustion on shared resource |

## Critical Files to Modify

1. `app/core/config/settings.py` - Add `orgs_db_url`
2. `app/core/providers.py` - Register new providers
3. `app/graphql/schemas/schema.py` - Extend Query type

## Verification

1. Run `task all` - type checks, linting, tests pass
2. Set `ORGS_DB_URL` in `.env.local`
3. Query `manufacturerSearch(searchTerm: "test")` via GraphQL playground
4. Verify only manufacturers returned (not other org types)
5. Verify deleted orgs are excluded
6. Test `active: false` returns pending manufacturers too

## Lessons Learned

### aioinject Union Type Limitation

aioinject cannot resolve `X | None` or `Optional[X]` types in Python 3.13. Attempting to use `Injected[ManufacturerService | None]` results in:

```
'types.UnionType' object has no attribute '__name__'
```

**Solution**: Make providers conditional at import time by checking `os.environ.get("ORGS_DB_URL")` before registering them. Then check the env var again at runtime in the resolver to return early if not configured.

### PostgreSQL Enum Types

The `org_type` and `status` columns in the external database use PostgreSQL enum types (`subscription.org_type`), not text columns. Direct comparison with Python strings fails:

```
operator does not exist: subscription.org_type = character varying
```

**Solution**: Cast the column to String in SQLAlchemy queries:

```python
from sqlalchemy import String, cast

stmt = select(RemoteOrg).where(
    cast(RemoteOrg.org_type, String) == OrgType.MANUFACTURER.value,
    cast(RemoteOrg.status, String) == OrgStatus.ACTIVE.value,
)
```

### Async Driver Requirement

SQLAlchemy's async extension requires an async-compatible driver. Using a standard `postgresql://` connection string fails:

```
sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver
```

**Solution**: Use the `asyncpg` driver in the connection string:

```
ORGS_DB_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

### Conditional Provider Registration

To support graceful degradation when `ORGS_DB_URL` is not set, providers are registered conditionally at module import time:

```python
# app/core/db/orgs_db_provider.py
providers: Iterable[aioinject.Provider[Any]] = []
if os.environ.get("ORGS_DB_URL"):
    providers = [
        aioinject.Singleton(create_orgs_db_engine),
        aioinject.Scoped(create_orgs_session),
    ]
```

This pattern is repeated in `repository_providers.py` and `service_providers.py`.
