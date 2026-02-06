# Backend Standards

This document defines Python/SQLAlchemy/GraphQL coding standards for the Flow Connect backend.

---

## Table of Contents

- [Models & Database](#models--database)
- [Code Patterns](#code-patterns)
- [Query Performance](#query-performance)
- [Dependency Injection](#dependency-injection)
- [Code Quality](#code-quality)
- [Type Safety](#type-safety)
- [Docstring Guidelines](#docstring-guidelines)
- [SOLID Principles](#solid-principles)
- [Architecture Patterns](#architecture-patterns)
- [Code Review Checklist](#code-review-checklist)
- [Common Anti-Patterns](#common-anti-patterns)

---

## Models & Database

### 1. Use MutableDict for JSON Columns

Always use `MutableDict` for JSON column types to enable SQLAlchemy mutation tracking:

```python
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import JSONB

metadata: Mapped[dict] = mapped_column(
    MutableDict.as_mutable(JSONB),
    default={},
)
```

**Why**: Without `MutableDict`, SQLAlchemy won't detect in-place mutations like `obj.metadata["key"] = value`.

### 2. Use PostgreSQL TIMESTAMP Instead of DateTime

Use `TIMESTAMP` for timestamp columns, not `DateTime`:

```python
from sqlalchemy import TIMESTAMP

created_at: Mapped[datetime] = mapped_column(
    TIMESTAMP(timezone=True),
    nullable=False,
    server_default=func.now(),
)
```

### 3. Define Scale and Precision for Numeric Fields

Always specify scale and precision for `Numeric` fields:

```python
from sqlalchemy import Numeric

amount: Mapped[Decimal] = mapped_column(
    Numeric(18, 6),  # 18 total digits, 6 decimal places
    nullable=False,
)
```

### 4. Update Alembic down_revision Before Merging

Before merging a PR with migrations, update `down_revision` to match the latest version in staging. This prevents migration conflicts when multiple PRs add migrations.

---

## Code Patterns

### 5. Inputs Must Inherit from BaseInput

All GraphQL input types must inherit from `BaseInput` (which implements `to_orm_object` and `to_orm_list`):

```python
@strawberry.input
class OrganizationInput(BaseInput):
    name: str
    status: str | None = strawberry.UNSET
```

### 6. Single Input Class for Create/Update

Use ONE input class for both create and update operations. Don't create separate `CreateInput` and `UpdateInput` classes:

```python
# GOOD: Single input class
@strawberry.input
class OrganizationInput(BaseInput):
    name: str
    status: str | None = strawberry.UNSET

# BAD: Separate classes with duplicated fields
class CreateOrganizationInput: ...
class UpdateOrganizationInput: ...
```

### 7. Use strawberry.UNSET for Optional Fields

Use `strawberry.UNSET` with optional fields instead of if/else chains:

```python
@strawberry.input
class UpdateInput(BaseInput):
    name: str | None = strawberry.UNSET
    status: str | None = strawberry.UNSET

# In service - UNSET fields are automatically skipped by to_orm_object()
entity = input.to_orm_object(Entity)
```

**Why**: `UNSET` distinguishes between "not provided" and "explicitly set to None".

### 8. Responses Must Inherit from DTOMixin

All GraphQL response types must inherit from `DTOMixin` for proper model-to-DTO conversion:

```python
@strawberry.type
class OrganizationResponse(DTOMixin):
    id: strawberry.ID
    name: str

    @classmethod
    def from_model(cls, model: Organization) -> "OrganizationResponse":
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name,
        )
```

### 9. Break Large Response Files

Don't put multiple response types in one file. Break large response files into separate files per type:

```
strawberry/
├── organization_types.py      # OrganizationResponse, OrganizationLiteResponse
├── member_types.py            # MemberResponse, MemberLiteResponse
└── connection_types.py        # ConnectionResponse
```

### 10. Move Activity Logging to Processors

Keep services focused on business logic. Move activity logging to processors (`after_create`, `after_update`):

```python
# GOOD: Service has single responsibility
class OrganizationService:
    async def create(self, data: OrganizationInput) -> Organization:
        return await self.repository.create(organization)
        # Logging handled by processor

# BAD: Service does too much
class OrganizationService:
    async def create(self, data: OrganizationInput) -> Organization:
        org = await self.repository.create(organization)
        await self.activity_service.log_creation(org)  # Wrong place
        return org
```

### 11. Don't Create Single-Use Functions

Don't extract queries or logic into separate functions if they're only used once. Keep them inline for readability:

```python
# GOOD: Query inline where used
async def get_active_members(self, org_id: uuid.UUID) -> list[Member]:
    stmt = select(Member).where(
        Member.org_id == org_id,
        Member.status == "active",
    )
    result = await self.session.execute(stmt)
    return list(result.scalars().all())

# BAD: Unnecessary abstraction for single use
def _build_active_members_query(org_id: uuid.UUID) -> Select:
    return select(Member).where(...)

async def get_active_members(self, org_id: uuid.UUID) -> list[Member]:
    stmt = self._build_active_members_query(org_id)
    ...
```

---

## Query Performance

### 12. Prefer joinedload Over selectinload

Use `joinedload` for relationships to reduce the number of SQL queries:

```python
# GOOD: Single query with JOIN
stmt = select(Organization).options(
    joinedload(Organization.members),
)

# LESS OPTIMAL: Separate SELECT query
stmt = select(Organization).options(
    selectinload(Organization.members),
)
```

**When to use selectinload**: Only when loading large collections where a JOIN would create too many duplicate rows.

### 13. Use lazy='noload' for Unused Relationships

Set `lazy='noload'` on relationships not typically needed to prevent unintended eager loading:

```python
class Organization(BaseModel):
    # Frequently needed - use default lazy loading
    members: Mapped[list["Member"]] = relationship()

    # Rarely needed - prevent accidental loading
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        lazy="noload",
    )
```

### 14. Avoid Multiple SQL Queries

Fetch all needed data in a single query instead of making multiple separate queries:

```python
# GOOD: Single query with all relationships
stmt = (
    select(Organization)
    .options(
        joinedload(Organization.members),
        joinedload(Organization.settings),
    )
    .where(Organization.id == org_id)
)

# BAD: Multiple queries
org = await self.get_org(org_id)
members = await self.get_members(org_id)  # Separate query
settings = await self.get_settings(org_id)  # Another query
```

---

## Dependency Injection

### 15. Place Injected Services at Beginning of Parameters

Never set injected services to `None`. Place them at the beginning of function parameters:

```python
# GOOD: Injected services first, no defaults
@strawberry.field()
@inject
async def get_organization(
    self,
    service: Injected[OrganizationService],  # First, no default
    org_id: strawberry.ID,
) -> OrganizationResponse | None:
    ...

# BAD: Injected service with None default
async def get_organization(
    self,
    org_id: strawberry.ID,
    service: Injected[OrganizationService] | None = None,  # Wrong
) -> OrganizationResponse | None:
    ...
```

### 16. No pyright: ignore for Injection Errors

Never use `# pyright: ignore` to bypass linter errors on improper injections. Fix the underlying issue instead:

```python
# BAD: Hiding the problem
service: Injected[OrganizationService] | None = None  # pyright: ignore

# GOOD: Proper injection without suppression
service: Injected[OrganizationService]
```

---

## Code Quality

### 17. Check for Circular Import References

Before submitting PRs, verify there are no circular import issues. The code must import and run without errors:

```bash
# Quick check - should not raise ImportError
python -c "from app.graphql.schemas.schema import schema"
```

**Common fixes**:
- Use lazy imports inside functions
- Move shared types to a separate module
- Use `TYPE_CHECKING` for type-only imports

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.graphql.organizations.models import Organization
```

---

## Type Safety

Every function parameter MUST have a type hint and every function MUST have a return type annotation.

Use Python 3.13 syntax:
- `list[str]` not `List[str]`
- `dict[str, Any]` not `Dict[str, Any]`
- `str | None` not `Optional[str]`
- `int | str` not `Union[int, str]`

---

## Docstring Guidelines

- Only add docstrings to PUBLIC functions/classes that are part of the API
- Do NOT add redundant docstrings that just repeat the function signature
- Good docstring: Explains WHY and provides context
- Bad docstring: Restates WHAT the code does (self-evident from type hints)

**Examples:**

```python
# BAD: Redundant docstring
async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
    """Get a job by ID."""  # This adds NO value
    return await self.repository.get_by_id(job_id)

# GOOD: No docstring needed - function is self-documenting
async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
    return await self.repository.get_by_id(job_id)

# GOOD: Docstring adds value
async def sync_emails(
    self,
    user_id: uuid.UUID,
    folder_ids: list[str] | None = None,
) -> AsyncGenerator[SyncProgressType, None]:
    """
    Sync emails for a user.
    Yields progress updates for real-time feedback.

    The sync pipeline:
    1. Validates user token
    2. Fetches emails from specified folders (or inbox by default)
    3. Maps to internal associations
    4. Creates records for tracking
    """
    ...
```

---

## SOLID Principles

### Single Responsibility Principle
- Each class/function has ONE reason to change
- Repositories: ONLY data access
- Services: ONLY business logic orchestration
- Models: ONLY data structure

### Open/Closed Principle
- Use Abstract Base Classes (ABC) for extensibility
- Strategy pattern for varying behavior
- Dependency injection for flexibility

### Liskov Substitution Principle
- Derived classes must be substitutable for base classes
- Don't strengthen preconditions or weaken postconditions

### Interface Segregation Principle
- Keep interfaces focused and minimal
- Don't force clients to depend on unused methods

### Dependency Inversion Principle
- Depend on abstractions (ABC), not concrete implementations
- All dependencies injected via constructor
- Use aioinject for dependency injection

---

## Architecture Patterns

### Repository Pattern
```python
class EntityRepository:
    def __init__(
        self,
        session: AsyncSession,
        auth_info: AuthInfo,
    ) -> None:
        self.session = session
        self.auth_info = auth_info

    async def create(self, entity: Entity) -> Entity:
        self.session.add(entity)
        await self.session.flush([entity])
        return entity

    async def get_by_id(
        self,
        entity_id: uuid.UUID,
        *,
        load_relations: bool = True,
    ) -> Entity | None:
        stmt = select(Entity).where(Entity.id == entity_id)
        if load_relations:
            stmt = stmt.options(
                joinedload(Entity.related),
            )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
```

### Service Pattern
```python
class EntityService:
    def __init__(
        self,
        repository: EntityRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def create(
        self,
        data: CreateEntityInput,
    ) -> Entity:
        # Orchestrate business logic
        ...
```

### Model Pattern
```python
from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column
from commons.db.v6 import BaseModel

class Entity(BaseModel):
    __tablename__ = "entities"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )
```

### GraphQL Resolver Pattern
```python
import strawberry
from app.graphql.di import inject, Injected

@strawberry.type
class Query:
    @strawberry.field
    @inject
    async def get_entity(
        self,
        entity_id: uuid.UUID,
        entity_service: Injected[EntityService],
    ) -> EntityType | None:
        entity = await entity_service.get_by_id(entity_id)
        if not entity:
            return None
        return EntityType.from_model(entity)
```

### GraphQL Response Types (DTOs)

All GraphQL types are DTOs (Data Transfer Objects). Use the `*Response` suffix to make this explicit:

- **`*LiteResponse`** - For list views and search results (summary data, fewer fields)
- **`*Response`** - For detail views (extends LiteResponse, adds relationships)

---

## Code Review Checklist

Before finalizing any code, verify:

- [ ] File is under 300 lines
- [ ] No `""""""` at file start
- [ ] All functions have type hints
- [ ] No redundant docstrings (only valuable ones)
- [ ] Uses Python 3.13 syntax (`list[str]`, `str | None`)
- [ ] Dependencies injected via constructor
- [ ] No global state or singletons
- [ ] Async/await for all I/O operations
- [ ] Proper error handling with specific exceptions
- [ ] Repository methods use `flush()` not `commit()`
- [ ] Service methods orchestrate, don't access DB directly
- [ ] Models use `Mapped[type]` syntax
- [ ] GraphQL resolvers use `@inject` decorator
- [ ] Enums for constants
- [ ] Dataclasses for data containers
- [ ] Pathlib for file operations
- [ ] F-strings for formatting
- [ ] `match/case` for complex conditionals
- [ ] `@staticmethod` for methods that don't use `self`
- [ ] **NEVER** ran `alembic upgrade` or any DB-altering command

---

## Common Anti-Patterns

1. **Long files**: Split at 300 lines
2. **Missing type hints**: Every parameter and return value
3. **Redundant docstrings**: Only document complex logic
4. **Global state**: Always use dependency injection
5. **Direct DB access in services**: Use repositories
6. **Committing in repositories**: Use `flush()` instead
7. **Old typing syntax**: Use Python 3.13 features
8. **Missing error handling**: Use specific exceptions
9. **Synchronous I/O**: Use async/await
10. **Magic values**: Use enums or constants
11. **Running database migrations**: NEVER run `alembic upgrade/downgrade` - only create migration files
