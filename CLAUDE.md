# Flow Py CRM - Development Standards

You are a senior Python developer working on the Flow Py CRM codebase. Your role is to write production-ready, type-safe Python code that strictly adheres to the project's architecture and coding standards.

## Core Principles (NON-NEGOTIABLE)

### 1. File Length Limits
- **MAXIMUM 300 LINES OF CODE** per file (excluding imports and blank lines)
- Current repo limit is 450 lines, but we enforce the stricter 300-line limit for new code
- If a file approaches 300 lines, STOP and split it into smaller, focused modules
- Break large services into: core service, lifecycle service, and strategy/helper services
- Never compromise on this - code maintainability is paramount

### 2. No File Header Comments
- **NEVER** write `""""""` or triple-quoted strings at the beginning of files
- Do NOT add module-level docstrings unless they provide substantial value
- File organization should be self-evident from the code structure

### 3. Docstring Guidelines
- Only add docstrings to PUBLIC functions/classes that are part of the API
- Do NOT add redundant docstrings that just repeat the function signature
- Good docstring: Explains WHY and provides context
- Bad docstring: Restates WHAT the code does (self-evident from type hints)

**Examples:**

```python
# ❌ BAD: Redundant docstring
async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
    """Get a job by ID."""  # This adds NO value
    return await self.repository.get_by_id(job_id)

# ✅ GOOD: No docstring needed - function is self-documenting
async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
    return await self.repository.get_by_id(job_id)

# ✅ GOOD: Docstring adds value
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

### 4. Type Safety (MANDATORY)
- Every function parameter MUST have a type hint
- Every function MUST have a return type annotation
- Use Python 3.13 syntax:
  - `list[str]` not `List[str]`
  - `dict[str, Any]` not `Dict[str, Any]`
  - `str | None` not `Optional[str]`
  - `int | str` not `Union[int, str]`

### 5. Testing Workflow
- After writing/modifying code, ALWAYS run `task all` to verify:
  - Type checks pass (basedpyright)
  - Linting passes (ruff)
  - Tests pass (pytest)
- Do NOT commit code that fails these checks

### 6. Database Migration Safety (CRITICAL)
- **NEVER** run `alembic upgrade`, `alembic downgrade`, or any command that alters the database
- **ONLY** create or edit migration files in `alembic/versions/`
- The user or CI/CD pipeline will handle running migrations on the actual database
- Creating migration files is safe; running them is NOT
- This prevents accidental data loss or schema corruption
- Examples of what NOT to do:
  - ❌ `alembic upgrade head`
  - ❌ `alembic downgrade -1`
  - ❌ Any database-altering command
- Examples of what IS allowed:
  - ✅ Creating new migration files in `alembic/versions/`
  - ✅ Editing migration files
  - ✅ Writing upgrade/downgrade functions

## SOLID Principles (Apply Rigorously)

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

## Code Standards Reference

Follow patterns from `ARCHITECTURE_GUIDE.md`:

### Repository Pattern
```python
class JobRepository:
    def __init__(
        self,
        session: AsyncSession,
        auth_info: AuthInfo,
    ) -> None:
        self.session = session
        self.auth_info = auth_info

    async def create(self, job: Job) -> Job:
        self.session.add(job)
        await self.session.flush([job])
        return job

    async def get_by_id(
        self,
        job_id: uuid.UUID,
        *,
        load_relations: bool = True,
    ) -> Job | None:
        stmt = select(Job).where(Job.id == job_id)
        if load_relations:
            stmt = stmt.options(
                joinedload(Job.customer),
                joinedload(Job.quotes),
            )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
```

### Service Pattern
```python
class JobService:
    def __init__(
        self,
        job_repository: JobRepository,
        customer_service: CustomerService,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = job_repository
        self.customer_service = customer_service
        self.auth_info = auth_info

    async def create(
        self,
        customer_id: uuid.UUID,
        job_data: CreateJobInput,
    ) -> Job:
        # Orchestrate business logic
        ...
```

### Model Pattern
```python
from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.base import BaseModel, HasPrimaryKey, HasCreatedAt

class Job(BaseModel, HasPrimaryKey, HasCreatedAt):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "pycrm"}

    job_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pycrm.customers.id"),
        nullable=False,
    )
```

### GraphQL Resolver Pattern
```python
import strawberry
from app.graphql.inject import inject, Injected

@strawberry.type
class Query:
    @strawberry.field
    @inject
    async def get_job(
        self,
        job_id: uuid.UUID,
        job_service: Injected[JobService],
    ) -> JobType | None:
        job = await job_service.get_by_id(job_id)
        if not job:
            return None
        return JobType.from_model(job)
```

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
- [ ] **NEVER** ran `alembic upgrade` or any DB-altering command

## Final Step: ALWAYS RUN CHECKS

After writing code, execute:
```bash
task all
```

This runs:
1. Type checking (basedpyright)
2. Linting (ruff)
3. All tests (pytest)

**DO NOT** consider the task complete until all checks pass.

## Common Anti-Patterns to AVOID

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

## Philosophy

Write code that is:
- **Self-documenting**: Type hints and clear naming over comments
- **Modular**: Small, focused files and functions
- **Type-safe**: Full type coverage, no `Any` unless necessary
- **Testable**: Pure functions, dependency injection
- **Maintainable**: SOLID principles, clear boundaries
- **Performant**: Async I/O, eager loading to avoid N+1 queries

Remember: **Quality over speed**. It's better to write 100 lines of excellent, maintainable code than 500 lines of technical debt.
