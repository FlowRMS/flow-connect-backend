# AI PR Review Guide - Flow Py Backend

This document provides comprehensive guidelines for AI systems reviewing Pull Requests in this repository. Use these rules to identify technical debt, bad practices, unnecessary code, and deviations from project standards.

---

## Quick Reference: Critical Violations

These are **immediate rejection criteria**. Flag these prominently:

| Violation | Severity |
|-----------|----------|
| File exceeds 300 lines of code | 🔴 CRITICAL |
| Missing type hints on function parameters or return types | 🔴 CRITICAL |
| Running `alembic upgrade/downgrade` commands | 🔴 CRITICAL |
| Using `commit()` in repositories instead of `flush()` | 🔴 CRITICAL |
| Module-level docstrings (`"""..."""` at file start) | 🟠 HIGH |
| Old typing syntax (`List[str]`, `Optional[str]`, `Union[...]`) | 🟠 HIGH |
| Direct database access in services | 🟠 HIGH |
| Global state or singletons | 🟠 HIGH |
| Synchronous I/O in async context | 🟠 HIGH |

---

## 1. File Structure & Organization

### 1.1 File Length (STRICT LIMIT)

**Rule:** Maximum **300 lines of code** per file (excluding imports and blank lines).

**Check for:**
- Files approaching or exceeding 300 lines
- Large classes that should be split
- Multiple concerns in a single file

**Acceptable splitting patterns:**
- Core service + lifecycle service + strategy/helper services
- Base repository + specialized repository extensions
- Query handlers split by operation type

**Flag:** "This file has X lines. Consider splitting into smaller, focused modules. Suggestion: [specific split recommendation]"

### 1.2 No Module-Level Docstrings

**Rule:** NEVER use `"""..."""` or triple-quoted strings at the beginning of files.

**Bad:**
```python
"""
This module handles user authentication.
"""

import ...
```

**Good:**
```python
import ...
```

**Flag:** "Remove the module-level docstring. File organization should be self-evident from the code structure."

### 1.3 Import Organization

**Expected order:**
1. Standard library imports
2. Third-party imports
3. Local application imports

**Check:** Imports should be sorted (enforced by ruff).

---

## 2. Type Safety (MANDATORY)

### 2.1 Type Hints Required

**Rule:** Every function parameter MUST have a type hint. Every function MUST have a return type annotation.

**Bad:**
```python
def get_user(user_id):
    ...

def process_data(items, options=None):
    return items
```

**Good:**
```python
def get_user(user_id: uuid.UUID) -> User | None:
    ...

def process_data(items: list[str], options: dict[str, Any] | None = None) -> list[str]:
    return items
```

**Flag:** "Missing type hint for parameter `X` / Missing return type annotation"

### 2.2 Python 3.13 Syntax (REQUIRED)

**Rule:** Use modern Python 3.13 typing syntax exclusively.

| ❌ Deprecated | ✅ Required |
|--------------|-------------|
| `List[str]` | `list[str]` |
| `Dict[str, Any]` | `dict[str, Any]` |
| `Set[int]` | `set[int]` |
| `Tuple[str, int]` | `tuple[str, int]` |
| `Optional[str]` | `str \| None` |
| `Union[int, str]` | `int \| str` |
| `from typing import List, Dict` | Remove these imports |

**Flag:** "Use Python 3.13 syntax: `X` should be `Y`"

### 2.3 Avoid `Any` Unless Necessary

**Rule:** Minimize use of `Any`. If used, it should be justified.

**Check for:**
- Overuse of `Any` type
- `Any` where a more specific type could be used
- `dict[str, Any]` where a TypedDict or dataclass is more appropriate

---

## 3. Documentation Standards

### 3.1 Docstring Guidelines

**Rule:** Only add docstrings to PUBLIC functions/classes that are part of the API, and only when they add value beyond the type hints.

**Bad (redundant):**
```python
async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
    """Get a job by ID."""
    return await self.repository.get_by_id(job_id)
```

**Good (self-documenting, no docstring needed):**
```python
async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
    return await self.repository.get_by_id(job_id)
```

**Good (docstring adds value):**
```python
async def sync_o365_emails(
    self,
    user_id: uuid.UUID,
    folder_ids: list[str] | None = None,
) -> AsyncGenerator[SyncProgressType, None]:
    """
    Sync emails from Microsoft 365 for a user.
    Yields progress updates for real-time feedback.

    The sync pipeline:
    1. Validates user O365 token
    2. Fetches emails from specified folders (or inbox by default)
    3. Maps to internal contact/job associations
    4. Creates note records for tracking
    """
    ...
```

**Flag when docstring:**
- Just restates the function name
- Only describes parameter types (already in type hints)
- Says "Returns X" when return type is obvious
- Adds no context about WHY or complex behavior

### 3.2 Comment Guidelines

**Rule:** Comments should explain WHY, not WHAT. Code should be self-documenting.

**Bad:**
```python
# Get the user from the database
user = await repository.get_by_id(user_id)

# Check if user exists
if user is None:
    raise NotFoundError("User not found")
```

**Good:**
```python
user = await repository.get_by_id(user_id)
if user is None:
    raise NotFoundError("User not found")

# Business rule: Users created before 2020 need migration
if user.created_at < MIGRATION_CUTOFF:
    await migrate_user_data(user)
```

---

## 4. Architectural Patterns

### 4.1 Repository Pattern

**Location:** `/app/graphql/[entity]/repositories/`

**Responsibilities:**
- Data access ONLY
- No business logic
- Use `flush()` not `commit()`
- Return domain models

**Required patterns:**
```python
class EntityRepository:
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        # Constructor injection for dependencies
        ...

    async def create(self, entity: Entity) -> Entity:
        self.session.add(entity)
        await self.session.flush([entity])  # NOT commit()
        return entity

    async def get_by_id(
        self,
        entity_id: uuid.UUID,
        *,
        options: list[ExecutableOption] | None = None,
    ) -> Entity | None:
        ...
```

**Flag:**
- `await self.session.commit()` → "Use `flush()` instead of `commit()`. Transaction management is handled at the context level."
- Business logic in repository → "Move business logic to service layer. Repository should only handle data access."
- Direct SQL without using repository base methods → "Consider using base repository methods for consistency."

### 4.2 Service Pattern

**Location:** `/app/graphql/[entity]/services/`

**Responsibilities:**
- Business logic orchestration
- Validation
- Coordinating repository calls
- Error handling

**Required patterns:**
```python
class EntityService:
    def __init__(
        self,
        repository: EntityRepository,
        other_service: OtherService,  # Inject services, not repositories for other entities
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.other_service = other_service
        self.auth_info = auth_info

    async def create_entity(
        self,
        input_data: CreateEntityInput,
    ) -> Entity:
        # Validation
        if not self._is_valid(input_data):
            raise ValidationError("...")

        # Business logic
        entity = input_data.to_orm_model()
        return await self.repository.create(entity)
```

**Flag:**
- Direct database access (using `session` directly) → "Services should use repositories for data access."
- Service calling another entity's repository directly → "Use the corresponding service instead of accessing the repository directly."
- Missing error handling for expected failure cases

### 4.3 GraphQL Resolver Pattern

**Location:** `/app/graphql/[entity]/queries/` and `/app/graphql/[entity]/mutations/`

**Required patterns:**
```python
@strawberry.type
class EntityQueries:
    @strawberry.field
    @inject
    async def entity(
        self,
        id: uuid.UUID,
        service: Injected[EntityService],
    ) -> EntityType | None:
        result = await service.get_by_id(id)
        if result is None:
            return None
        return EntityType.from_orm_model(result)
```

**Flag:**
- Missing `@inject` decorator when using `Injected[...]`
- Business logic in resolvers → "Move business logic to service layer."
- Direct repository access in resolvers → "Use service layer for data access."

### 4.4 Input/Output Type Pattern

**GraphQL Input:**
```python
@strawberry.input
class EntityInput(BaseInputGQL[Entity]):
    required_field: str
    optional_field: str | None = strawberry.UNSET

    def to_orm_model(self) -> Entity:
        return Entity(
            required_field=self.required_field,
            optional_field=self.optional_field(self.optional_field),
        )
```

**GraphQL Output Type:**
```python
@strawberry.type
class EntityType(DTOMixin[Entity]):
    id: uuid.UUID
    name: str

    @classmethod
    def from_orm_model(cls, model: Entity) -> Self:
        return cls(
            id=model.id,
            name=model.name,
        )
```

**Flag:**
- Not extending `BaseInputGQL` for inputs
- Not extending `DTOMixin` for output types
- Missing `to_orm_model()` or `from_orm_model()` methods

---

## 5. Dependency Injection

### 5.1 Constructor Injection (REQUIRED)

**Rule:** All dependencies must be injected via constructor.

**Bad:**
```python
class UserService:
    def __init__(self) -> None:
        self.repository = UserRepository()  # Creating instance directly
        self.settings = get_settings()  # Global function call
```

**Good:**
```python
class UserService:
    def __init__(
        self,
        repository: UserRepository,
        settings: Settings,
    ) -> None:
        self.repository = repository
        self.settings = settings
```

**Flag:** "Use constructor injection. Do not instantiate dependencies directly or use global functions."

### 5.2 Provider Registration

**Check that new services/repositories are registered in:**
- `/app/core/providers.py`
- `/app/graphql/service_providers.py`
- `/app/graphql/repositories.py`

**Flag:** "New service/repository appears to be unregistered in the DI container."

---

## 6. Error Handling

### 6.1 Use Specific Exceptions

**Available exceptions in `/app/errors/`:**
- `NotFoundError` - Entity not found
- `ConflictError` - Duplicate or conflicting state
- `ValidationError` - Invalid input
- `UnauthorizedError` - Permission denied
- `DeletionError` - Cannot delete entity

**Bad:**
```python
if user is None:
    raise Exception("User not found")
```

**Good:**
```python
from app.errors import NotFoundError

if user is None:
    raise NotFoundError(f"User with ID {user_id} not found")
```

**Flag:** "Use specific exception types from `/app/errors/` instead of generic exceptions."

### 6.2 Don't Swallow Exceptions

**Bad:**
```python
try:
    await risky_operation()
except Exception:
    pass  # Silent failure
```

**Good:**
```python
try:
    await risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

---

## 7. Async/Await Patterns

### 7.1 Async for All I/O

**Rule:** All I/O operations must use async/await.

**Bad:**
```python
def get_user(user_id: uuid.UUID) -> User | None:
    # Blocking call in async context
    response = requests.get(f"/users/{user_id}")
    return response.json()
```

**Good:**
```python
async def get_user(user_id: uuid.UUID) -> User | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return response.json()
```

**Flag:** "Use async I/O. Blocking calls in async context can cause performance issues."

### 7.2 Proper Async Generator Usage

```python
async def stream_items(self) -> AsyncGenerator[Item, None]:
    async for item in self.repository.stream_all():
        yield item
```

---

## 8. Database Patterns

### 8.1 NEVER Run Migrations

**Rule:** NEVER execute `alembic upgrade`, `alembic downgrade`, or any database-altering command.

**Allowed:**
- Creating new migration files in `/alembic/versions/`
- Editing migration files
- Writing upgrade/downgrade functions

**NOT Allowed:**
- `alembic upgrade head`
- `alembic downgrade -1`
- Any command that modifies the database schema

**Flag:** "🔴 CRITICAL: Never run alembic upgrade/downgrade. Only create/edit migration files."

### 8.2 Use Eager Loading

**Rule:** Prevent N+1 queries by eager loading relationships.

**Bad:**
```python
async def get_jobs(self) -> list[Job]:
    jobs = await self.repository.list_all()
    for job in jobs:
        # N+1 query!
        customer = await self.customer_repository.get_by_id(job.customer_id)
```

**Good:**
```python
async def get_jobs(self) -> list[Job]:
    return await self.repository.list_all(
        options=[
            joinedload(Job.customer),
            joinedload(Job.quotes),
        ]
    )
```

**Flag:** "Potential N+1 query. Consider using eager loading with `joinedload()` or `selectinload()`."

### 8.3 Session Management

- Use `flush()` in repositories, not `commit()`
- Transaction boundaries are managed by context managers
- Don't store session in instance variables beyond constructor

---

## 9. Code Quality Anti-Patterns

### 9.1 Over-Engineering

**Flag these patterns:**

| Pattern | Why It's Bad |
|---------|--------------|
| Feature flags for one-time changes | Just change the code |
| Backward-compatibility shims for unused code | Delete unused code |
| Abstract base class with only one implementation | Premature abstraction |
| Config options for things that never change | Unnecessary complexity |
| Error handling for impossible cases | Trust internal code |

**Example of over-engineering:**
```python
# Bad: Unnecessary abstraction
class UserFetchStrategy(ABC):
    @abstractmethod
    async def fetch(self, user_id: UUID) -> User: ...

class DatabaseUserFetchStrategy(UserFetchStrategy):
    async def fetch(self, user_id: UUID) -> User:
        return await self.repository.get_by_id(user_id)

# Good: Simple and direct
async def get_user(self, user_id: UUID) -> User:
    return await self.repository.get_by_id(user_id)
```

### 9.2 Dead Code

**Flag:**
- Commented-out code blocks
- Unused imports
- Unused variables (unless intentionally `_`-prefixed)
- Functions that are never called
- `# TODO: remove this` comments

### 9.3 Magic Values

**Bad:**
```python
if status == 1:  # What does 1 mean?
    ...
```

**Good:**
```python
from app.enums import JobStatus

if status == JobStatus.PENDING:
    ...
```

**Flag:** "Use enums or named constants instead of magic values."

### 9.4 Backward-Compatibility Hacks

**Flag these patterns:**
```python
# Bad: Renaming to unused
_old_var = new_var  # For backward compatibility

# Bad: Re-exporting for compatibility
from .new_module import function as old_function

# Bad: Placeholder comments
# removed: old_function()
```

**Rule:** If something is unused, delete it completely.

---

## 10. Security Checks

### 10.1 OWASP Top 10

**Check for:**
- SQL injection (raw SQL without parameterization)
- Command injection (unsanitized shell commands)
- XSS vulnerabilities (in any response generation)
- Insecure deserialization
- Sensitive data exposure (logging passwords, tokens)

### 10.2 Secrets Detection

**Flag:**
- Hardcoded API keys, passwords, tokens
- Committing `.env` files
- Credentials in code comments
- Connection strings with embedded credentials

### 10.3 Input Validation

**Check for:**
- Unvalidated user input passed to queries
- Missing bounds checking on arrays/lists
- Unchecked type conversions

---

## 11. Testing Requirements

### 11.1 Test Coverage

**New code should include tests for:**
- Happy path scenarios
- Edge cases
- Error conditions
- Business rule validation

### 11.2 Test Patterns

**Good test structure:**
```python
class TestEntityService:
    async def test_create_entity_success(self) -> None:
        """Test creating an entity with valid input."""
        ...

    async def test_create_entity_duplicate_fails(self) -> None:
        """Test that duplicate entities raise ConflictError."""
        ...
```

**Flag:**
- No tests for new functionality
- Tests that only test the happy path
- Tests without assertions
- Tests with `# type: ignore` without justification

---

## 12. PR Review Checklist

Use this checklist for every PR:

### Critical (Must Fix)
- [ ] All files under 300 lines
- [ ] All functions have type hints (parameters + return)
- [ ] Using Python 3.13 syntax (`list[str]`, `str | None`)
- [ ] No `alembic upgrade/downgrade` commands
- [ ] Repositories use `flush()` not `commit()`

### High Priority (Should Fix)
- [ ] No module-level docstrings
- [ ] Only valuable docstrings (not redundant)
- [ ] Dependencies injected via constructor
- [ ] Services don't access DB directly
- [ ] Async/await for all I/O
- [ ] Proper error handling with specific exceptions
- [ ] No magic values (use enums/constants)
- [ ] No dead or commented-out code

### Medium Priority (Consider)
- [ ] New services/repositories registered in DI container
- [ ] Eager loading to prevent N+1 queries
- [ ] Tests included for new functionality
- [ ] No over-engineering or premature abstraction
- [ ] Clear separation of concerns

### Low Priority (Nice to Have)
- [ ] Consistent naming conventions
- [ ] Import order correct
- [ ] Logging follows project patterns

---

## 13. Review Output Format

When reviewing a PR, structure your feedback as:

```markdown
## PR Review Summary

### 🔴 Critical Issues (Must Fix)
- [file:line] Issue description
  - Suggestion: How to fix

### 🟠 High Priority Issues
- [file:line] Issue description
  - Suggestion: How to fix

### 🟡 Medium Priority Issues
- [file:line] Issue description
  - Suggestion: How to fix

### 💡 Suggestions
- [file:line] Improvement suggestion

### ✅ What's Good
- Positive aspects of the PR
```

---

## 14. Common Patterns Reference

### Standard Import Block
```python
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.errors import NotFoundError, ValidationError

if TYPE_CHECKING:
    from app.graphql.entity.repositories import EntityRepository
```

### Standard Repository Method
```python
async def get_by_id(
    self,
    entity_id: uuid.UUID,
    *,
    options: list[ExecutableOption] | None = None,
) -> Entity | None:
    stmt = select(Entity).where(Entity.id == entity_id)
    if options:
        stmt = stmt.options(*options)
    result = await self.session.execute(stmt)
    return result.unique().scalar_one_or_none()
```

### Standard Service Method
```python
async def create(
    self,
    input_data: CreateEntityInput,
) -> Entity:
    # Validation
    existing = await self.repository.get_by_name(input_data.name)
    if existing:
        raise ConflictError(f"Entity with name '{input_data.name}' already exists")

    # Create
    entity = input_data.to_orm_model()
    entity.created_by_id = self.auth_info.user_id
    return await self.repository.create(entity)
```

### Standard Resolver
```python
@strawberry.field
@inject
async def entity(
    self,
    id: uuid.UUID,
    service: Injected[EntityService],
) -> EntityType | None:
    result = await service.get_by_id(id)
    return EntityType.from_orm_model(result) if result else None
```

---

## 15. Project-Specific Terminology

| Term | Definition |
|------|------------|
| `ContextWrapper` | Multi-tenant context manager |
| `AuthInfo` | Current authenticated user info |
| `BaseInputGQL` | Base class for GraphQL inputs |
| `DTOMixin` | Base class for GraphQL output types |
| `Injected[T]` | Type wrapper for DI injection |
| `EntityProcessor` | Lifecycle hooks for entities |
| `RBAC` | Role-based access control |
| `TaskIQ` | Background task queue system |

---

## 16. File Locations Reference

| What | Where |
|------|-------|
| Entity Repository | `/app/graphql/[entity]/repositories/[entity]_repository.py` |
| Entity Service | `/app/graphql/[entity]/services/[entity]_service.py` |
| GraphQL Input | `/app/graphql/[entity]/strawberry/[entity]_input.py` |
| GraphQL Type | `/app/graphql/[entity]/strawberry/[entity]_response.py` |
| GraphQL Queries | `/app/graphql/[entity]/queries/[entity]_queries.py` |
| GraphQL Mutations | `/app/graphql/[entity]/mutations/[entity]_mutations.py` |
| DI Providers | `/app/core/providers.py` |
| Service Registration | `/app/graphql/service_providers.py` |
| Repository Registration | `/app/graphql/repositories.py` |
| Custom Exceptions | `/app/errors/` |
| Settings | `/app/core/config/` |
| Migrations | `/alembic/versions/` |
| Tests | `/tests/` |

---

## Final Notes

- **Quality over speed**: It's better to request changes than to approve problematic code
- **Be specific**: Point to exact lines and provide concrete fix suggestions
- **Explain why**: Help the author understand the reasoning behind feedback
- **Acknowledge good work**: Note well-written code and good practices
- **Consider context**: Some rules may have valid exceptions in specific cases

This guide should be used in conjunction with the project's `CLAUDE.md` and `ARCHITECTURE_GUIDE.md` for complete context.
