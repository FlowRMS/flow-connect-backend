# Flow AI Architecture Guide

## Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [API Architecture](#api-architecture)
- [Database Patterns](#database-patterns)
- [Service Layer Patterns](#service-layer-patterns)
- [Agent Patterns](#agent-patterns)
- [Code Style Guidelines](#code-style-guidelines)
- [Naming Conventions](#naming-conventions)
- [File Organization](#file-organization)
- [Dependency Injection](#dependency-injection)
- [Testing Guidelines](#testing-guidelines)
- [Deployment](#deployment)

---

## Overview

Flow AI is a scalable, AI-powered document processing platform built with FastAPI, GraphQL, and SQLAlchemy. The architecture follows **Clean Architecture** and **Domain-Driven Design** principles with clear separation between layers.

### Core Architectural Principles

1. **Dependency Injection**: All dependencies injected via `aioinject` - no global state
2. **Async First**: All I/O operations use async/await
3. **Type Safety**: Full type hints throughout, leveraging Python 3.13 features
4. **Multi-tenancy**: Built-in tenant isolation at database and application layers
5. **Auto-discovery**: Services, repositories, and agents auto-registered
6. **GraphQL Subscriptions**: Real-time updates via async generators
7. **AI Agent Integration**: Structured outputs via `pydantic-ai`
8. **Sandbox Execution**: Safe code execution via Daytona
9. **Serverless Jobs**: Modal.com for heavy computations

---

## Technology Stack

### Core Framework
- **Python 3.13+**: Latest Python features (PEP 585 type hints, pattern matching)
- **FastAPI**: Web framework for high-performance async APIs
- **Strawberry GraphQL**: GraphQL library with full type safety
- **SQLAlchemy 2.0**: Modern async ORM with declarative base
- **Alembic**: Database migrations
- **PostgreSQL**: Primary database with multi-tenant support

### AI & ML
- **pydantic-ai**: Structured AI agent outputs
- **OpenAI & Anthropic**: LLM providers
- **Qdrant**: Vector database for embeddings
- **Voyage AI**: Embedding generation

### Data Processing
- **Polars**: High-performance data processing
- **Pandas**: Data manipulation
- **DuckDB**: In-process analytical database
- **Daytona**: Secure sandbox for code execution

### Infrastructure
- **UV**: Fast Python package manager
- **aioinject**: Async dependency injection
- **Modal**: Serverless compute platform
- **Redis**: Caching layer
- **Datadog**: Observability and logging

### Development Tools
- **Ruff**: Fast Python linter
- **Basedpyright**: Type checker
- **pytest**: Testing framework
- **pre-commit**: Git hooks for code quality

---

## Project Structure

```
flow-py-crm/
├── app/                          # Main application code
│   ├── agents/                   # AI agent implementations
│   │   ├── {agent_name}/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py         # Agent class
│   │   │   ├── models/          # Pydantic I/O models
│   │   │   │   └── models.py
│   │   │   └── prompts/         # LLM prompts
│   │   │       └── prompt.py
│   │   ├── tabular_agent/
│   │   ├── dto_agent/
│   │   ├── pdf_to_markdown_agent/
│   │   └── base_agent.py        # Shared agent utilities
│   │
│   ├── api/                      # FastAPI application
│   │   └── app.py               # App factory & middleware
│   │
│   ├── auth/                     # Authentication
│   │   └── providers/           # Keycloak, JWT providers
│   │
│   ├── core/                     # Core infrastructure
│   │   ├── config/              # Settings & configuration
│   │   │   └── settings.py
│   │   ├── container.py         # DI container setup
│   │   ├── context.py           # Request context
│   │   ├── db/                  # Database setup
│   │   │   ├── base.py          # Base models
│   │   │   └── db_provider.py   # Session management
│   │   └── providers.py         # Provider registration
│   │
│   ├── files/                    # File handling
│   │   └── services/
│   │       └── file_info_service.py
│   │
│   ├── graphql/                  # GraphQL API layer
│   │   ├── schemas/             # Schema definitions
│   │   │   ├── schema.py        # Main schema
│   │   │   └── scalars.py       # Custom scalars
│   │   │
│   │   ├── {domain}/            # Domain module (e.g., document_processing)
│   │   │   ├── models/          # SQLAlchemy models
│   │   │   │   ├── __init__.py
│   │   │   │   └── {model}.py
│   │   │   ├── repositories/    # Data access layer
│   │   │   │   └── {model}_repository.py
│   │   │   ├── services/        # Business logic
│   │   │   │   └── {service}_service.py
│   │   │   ├── types/           # GraphQL types
│   │   │   │   └── {type}_types.py
│   │   │   ├── queries/         # Query resolvers
│   │   │   │   └── {domain}_queries.py
│   │   │   ├── mutations/       # Mutation resolvers
│   │   │   │   └── {domain}_mutations.py
│   │   │   └── subscriptions/   # Subscription resolvers
│   │   │       └── {domain}_subscriptions.py
│   │   │
│   │   ├── document_processing/  # Example domain
│   │   ├── documents/
│   │   └── inject.py            # DI utilities for GraphQL
│   │
│   └── wrappers/                 # External API wrappers
│       └── {service}_wrapper.py
│
├── alembic/                      # Database migrations
│   ├── versions/
│   └── env.py
│
├── jobs/                         # Modal serverless jobs
│   └── {job_name}.py
│
├── scripts/                      # Utility scripts
│
├── data/                         # Sample/test data
│
├── .k8s/                         # Kubernetes configs
│
├── pyproject.toml                # Project config & dependencies
├── uv.lock                       # Dependency lock file
├── alembic.ini                   # Alembic configuration
├── main.py                       # Development entry point
├── CLAUDE.md                     # Codebase instructions for AI
└── README.md                     # Project documentation
```

### Domain Module Structure

Each GraphQL domain follows this consistent structure:

```
app/graphql/{domain}/
├── models/                       # Database models (SQLAlchemy)
│   ├── __init__.py              # Export all models
│   ├── {entity}.py              # One file per entity
│   └── {entity}_relation.py     # Related entities
│
├── repositories/                 # Data access layer
│   ├── __init__.py
│   └── {entity}_repository.py   # One repository per model
│
├── services/                     # Business logic layer
│   ├── __init__.py
│   ├── {entity}_service.py      # Core service
│   ├── {entity}_lifecycle_service.py  # State management
│   └── {specialized}_service.py # Strategy/helper services
│
├── types/                        # GraphQL types (Strawberry)
│   ├── __init__.py
│   └── {entity}_types.py        # Types for entity
│
├── queries/                      # Query resolvers
│   ├── __init__.py
│   └── {domain}_queries.py
│
├── mutations/                    # Mutation resolvers
│   ├── __init__.py
│   └── {domain}_mutations.py
│
├── subscriptions/                # Subscription resolvers (optional)
│   ├── __init__.py
│   └── {domain}_subscriptions.py
│
├── enums.py                      # Domain-specific enums
└── __init__.py
```

---

## API Architecture

### FastAPI Application Setup

**Entry Point**: `app/api/app.py`

```python
def create_app() -> FastAPI:
    # Create DI container
    container = create_container()

    # Setup async lifespan
    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        configure_mappers()  # SQLAlchemy setup
        async with container:
            async with container.context() as ctx:
                settings = await ctx.resolve(Settings)
                setup_logging(...)
            yield

    # Create app with config
    app = FastAPI(
        title="Flow AI Backend API",
        description="Backend API for Flow AI",
        version="0.0.1",
        lifespan=lifespan,
        openapi_url=None,
    )

    # Add middleware
    app.add_middleware(AioInjectMiddleware, container=container)
    app.add_middleware(CORSMiddleware, ...)

    # Add custom middleware
    @app.middleware("http")
    async def add_process_time_header(request, call_next):
        # Track request timing
        ...

    # Include GraphQL router
    app.include_router(create_graphql_app(), prefix="/graphql")

    # Health check endpoint
    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    return app
```

### GraphQL Schema Organization

**Main Schema**: `app/graphql/schemas/schema.py`

```python
import strawberry
from app.graphql.document_processing.queries import DocumentQueries
from app.graphql.document_processing.mutations import DocumentMutations
from app.graphql.document_processing.subscriptions import DocumentSubscriptions

@strawberry.type
class Query:
    # Extend with domain queries
    document: DocumentQueries = strawberry.field()

@strawberry.type
class Mutation:
    # Extend with domain mutations
    document: DocumentMutations = strawberry.field()

@strawberry.type
class Subscription:
    # Extend with domain subscriptions
    document: DocumentSubscriptions = strawberry.field()

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
```

### Custom Scalars

Define custom scalars for common types:

```python
# app/graphql/schemas/scalars.py
import strawberry
from decimal import Decimal
import uuid
import datetime

JSON = strawberry.scalar(
    typing.Any,
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

UUID = strawberry.scalar(
    uuid.UUID,
    serialize=lambda v: str(v),
    parse_value=lambda v: uuid.UUID(v),
)

DateTime = strawberry.scalar(
    datetime.datetime,
    serialize=lambda v: v.isoformat(),
    parse_value=lambda v: datetime.datetime.fromisoformat(v),
)

DecimalScalar = strawberry.scalar(
    Decimal,
    serialize=lambda v: str(v),
    parse_value=lambda v: Decimal(v),
)
```

### Query Pattern

**Location**: `app/graphql/{domain}/queries/{domain}_queries.py`

```python
import strawberry
import uuid
from app.graphql.inject import inject, Injected
from app.graphql.document_processing.repositories import PendingDocumentRepository
from app.graphql.document_processing.types import PendingDocumentType

@strawberry.type
class DocumentQueries:
    @strawberry.field
    @inject
    async def get_pending_document(
        self,
        pending_id: uuid.UUID,
        # Inject dependencies
        pending_document_repository: Injected[PendingDocumentRepository],
    ) -> PendingDocumentType | None:
        """Get a pending document by ID."""
        document = await pending_document_repository.get_by_id(pending_id)
        if not document:
            return None
        return PendingDocumentType.from_model(document)

    @strawberry.field
    @inject
    async def list_pending_documents(
        self,
        cluster_id: uuid.UUID,
        pending_document_repository: Injected[PendingDocumentRepository],
    ) -> list[PendingDocumentType]:
        """List all pending documents in a cluster."""
        documents = await pending_document_repository.get_by_cluster(cluster_id)
        return [PendingDocumentType.from_model(doc) for doc in documents]
```

### Mutation Pattern

**Location**: `app/graphql/{domain}/mutations/{domain}_mutations.py`

```python
import strawberry
import uuid
from app.graphql.inject import inject, Injected
from app.graphql.document_processing.services import PendingDocumentService
from app.graphql.document_processing.types import PendingDocumentType

@strawberry.input
class CreatePendingDocumentInput:
    file_id: uuid.UUID
    cluster_id: uuid.UUID
    instructions: list[str] | None = None

@strawberry.type
class DocumentMutations:
    @strawberry.mutation
    @inject
    async def create_pending_document(
        self,
        input: CreatePendingDocumentInput,
        pending_document_service: Injected[PendingDocumentService],
    ) -> PendingDocumentType:
        """Create a new pending document."""
        document = await pending_document_service.create(
            file_id=input.file_id,
            cluster_id=input.cluster_id,
            instructions=input.instructions,
        )
        return PendingDocumentType.from_model(document)

    @strawberry.mutation
    @inject
    async def delete_pending_document(
        self,
        pending_id: uuid.UUID,
        pending_document_service: Injected[PendingDocumentService],
    ) -> bool:
        """Delete a pending document."""
        await pending_document_service.delete(pending_id)
        return True
```

### Subscription Pattern

**Location**: `app/graphql/{domain}/subscriptions/{domain}_subscriptions.py`

```python
import strawberry
import uuid
from collections.abc import AsyncGenerator
from app.graphql.inject import inject, Injected
from app.graphql.document_processing.services import PendingDocumentService
from app.graphql.document_processing.types import ProcessingProgressType

@strawberry.type
class DocumentSubscriptions:
    @strawberry.subscription
    @inject
    async def process_document_for_review(
        self,
        file_id: uuid.UUID,
        initial_instructions: list[str] | None = None,
        context_files: list[uuid.UUID] | None = None,
        pending_document_service: Injected[PendingDocumentService],
    ) -> AsyncGenerator[ProcessingProgressType, None]:
        """
        Subscribe to document processing progress.
        Yields progress updates as the document is processed.
        """
        async for progress in pending_document_service.process_and_stage(
            file_id=file_id,
            initial_instructions=initial_instructions,
            context_files=context_files,
        ):
            yield progress
```

**Key Points**:
- Subscriptions use `AsyncGenerator` for streaming updates
- Use `async for` to yield progress incrementally
- Perfect for long-running operations

---

## Database Patterns

### Model Definition

**Base Models**: `app/core/db/base.py`

```python
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, AsyncAttrs, Mapped, mapped_column
from sqlalchemy import UUID, TIMESTAMP, func
import uuid
import datetime

class Base(DeclarativeBase):
    """Base for all SQLAlchemy models."""
    pass

class BaseModel(Base, MappedAsDataclass, AsyncAttrs):
    """Base model with dataclass and async attributes."""
    __abstract__ = True

class HasPrimaryKey(MappedAsDataclass):
    """Mixin for UUID primary key."""
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default_factory=uuid.uuid4,
        init=False,
        primary_key=True,
    )

class HasCreatedAt(MappedAsDataclass):
    """Mixin for created_at timestamp."""
    __abstract__ = True

    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),
    )

class HasUpdatedAt(MappedAsDataclass):
    """Mixin for updated_at timestamp."""
    __abstract__ = True

    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
```

### Entity Model Pattern

**Location**: `app/graphql/{domain}/models/{entity}.py`

```python
from sqlalchemy import UUID, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.core.db.base import BaseModel, HasPrimaryKey, HasCreatedAt

class PendingDocument(BaseModel, HasPrimaryKey, HasCreatedAt):
    """Pending document awaiting processing."""

    __tablename__ = "pending_documents"
    __table_args__ = {"schema": "ai"}  # All tables in 'ai' schema

    # Columns with modern Mapped syntax
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai.document_clusters.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    instructions: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Relationships
    cluster: Mapped["DocumentCluster | None"] = relationship(
        init=False,
        back_populates="pending_documents",
        lazy="select",  # Lazy load by default
    )

    pages: Mapped[list["PendingDocumentPage"]] = relationship(
        init=False,
        back_populates="pending_document",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # String representation
    def __repr__(self) -> str:
        return f"<PendingDocument(id={self.id}, file_id={self.file_id})>"
```

**Key Features**:
- Use `Mapped[type]` for all columns (SQLAlchemy 2.0)
- Use `MappedAsDataclass` for automatic `__init__` generation
- Use `AsyncAttrs` for async relationship loading
- Always specify `schema="ai"` in `__table_args__`
- Use type unions for nullable fields: `type | None`
- Set `init=False` for relationships (not in constructor)

### Repository Pattern

**Location**: `app/graphql/{domain}/repositories/{entity}_repository.py`

```python
import uuid
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from commons.auth import AuthInfo
from app.graphql.document_processing.models import PendingDocument

class PendingDocumentRepository:
    """Repository for pending document data access."""

    def __init__(
        self,
        session: AsyncSession,
        auth_info: AuthInfo,
    ) -> None:
        self.session = session
        self.auth_info = auth_info

    async def create(self, pending_document: PendingDocument) -> PendingDocument:
        """Create a new pending document."""
        self.session.add(pending_document)
        await self.session.flush([pending_document])
        return pending_document

    async def get_by_id(
        self,
        pending_id: uuid.UUID,
        *,
        load_relations: bool = True,
    ) -> PendingDocument | None:
        """Get pending document by ID with optional eager loading."""
        stmt = select(PendingDocument).where(PendingDocument.id == pending_id)

        if load_relations:
            stmt = stmt.options(
                joinedload(PendingDocument.cluster),
                selectinload(PendingDocument.pages),
                selectinload(PendingDocument.correction_changes),
            )

        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_cluster(
        self,
        cluster_id: uuid.UUID,
    ) -> list[PendingDocument]:
        """Get all pending documents in a cluster."""
        stmt = (
            select(PendingDocument)
            .where(PendingDocument.cluster_id == cluster_id)
            .order_by(PendingDocument.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        pending_id: uuid.UUID,
        status: str,
    ) -> None:
        """Update document status."""
        stmt = (
            update(PendingDocument)
            .where(PendingDocument.id == pending_id)
            .values(status=status)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete(self, pending_id: uuid.UUID) -> None:
        """Delete a pending document."""
        stmt = delete(PendingDocument).where(PendingDocument.id == pending_id)
        await self.session.execute(stmt)
        await self.session.flush()
```

**Repository Guidelines**:
- One repository per model
- Inject `AsyncSession` and `AuthInfo`
- Use `flush()` instead of `commit()` (transaction managed at higher level)
- Use eager loading (`joinedload`, `selectinload`) to avoid N+1 queries
- Provide `load_relations` flag for optional eager loading
- Use SQLAlchemy 2.0 `select()` syntax
- Return `None` for not found, don't raise exceptions
- Use keyword-only arguments (`*`) for optional params

### Migration Pattern

**Alembic Configuration**: `alembic.ini`

```ini
[alembic]
script_location = alembic
version_table_schema = ai
version_table = alembic_version
file_template = %%(year)d%%(month).2d%%(day).2d_%%(slug)s
```

**Creating Migrations**:

```bash
# Auto-generate migration
uv run alembic revision --autogenerate -m "add_pending_document_table"

# Manual migration
uv run alembic revision -m "add_custom_index"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

**Migration File Pattern**:

```python
"""Add pending document table

Revision ID: 001_pending_document
Revises:
Create Date: 2025-01-15
"""
from typing import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_pending_document'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table(
        'pending_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cluster_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['cluster_id'],
            ['ai.document_clusters.id'],
            ondelete='CASCADE',
        ),
        schema='ai',
    )
    op.create_index(
        'ix_ai_pending_documents_file_id',
        'pending_documents',
        ['file_id'],
        schema='ai',
    )

def downgrade() -> None:
    op.drop_index('ix_ai_pending_documents_file_id', schema='ai')
    op.drop_table('pending_documents', schema='ai')
```

---

## Service Layer Patterns

### Service Organization

Services are organized by responsibility:

1. **Core Services**: Main business logic orchestration
2. **Lifecycle Services**: Entity state management
3. **Strategy Services**: Strategy pattern implementations
4. **Helper Services**: Specialized utility functions

### Core Service Pattern

**Location**: `app/graphql/{domain}/services/{entity}_service.py`

```python
import uuid
from collections.abc import AsyncGenerator
from commons.auth import AuthInfo
from loguru import logger
from app.graphql.document_processing.repositories import PendingDocumentRepository
from app.graphql.document_processing.models import PendingDocument
from app.graphql.document_processing.types import ProcessingProgressType

class PendingDocumentService:
    """Service for pending document business logic."""

    def __init__(
        self,
        # Inject all dependencies
        pending_document_repository: PendingDocumentRepository,
        document_processing_service: DocumentProcessingStrategyService,
        preprocessing_service: PreprocessingService,
        cluster_context_service: ClusterContextService,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = pending_document_repository
        self.processing_service = document_processing_service
        self.preprocessing_service = preprocessing_service
        self.cluster_context_service = cluster_context_service
        self.auth_info = auth_info

    async def process_and_stage(
        self,
        file_id: uuid.UUID,
        initial_instructions: list[str] | None = None,
        context_files: list[uuid.UUID] | None = None,
    ) -> AsyncGenerator[ProcessingProgressType, None]:
        """
        Process a file and stage it as a pending document.
        Yields progress updates for real-time feedback.
        """
        logger.info(f"Processing file {file_id}")

        # Yield progress updates
        yield ProcessingProgressType(
            action="Retrieving file information",
            pending_document=None,
        )

        # Get file info
        file_info = await self.processing_service.get_file_info(file_id)

        # Process context files if provided
        context_text = None
        if context_files:
            yield ProcessingProgressType(
                action=f"Converting {len(context_files)} context files",
                pending_document=None,
            )
            context_text = await self.cluster_context_service.convert_files(
                context_files
            )

        # Get processing strategy
        strategy = self.processing_service.get_strategy(file_info.file_type)

        yield ProcessingProgressType(
            action="Processing document",
            pending_document=None,
        )

        # Execute processing
        result = await strategy.process(
            file_info=file_info,
            instructions=initial_instructions,
            context=context_text,
        )

        # Create pending document
        pending_doc = PendingDocument(
            file_id=file_id,
            status="staged",
            instructions=initial_instructions,
        )
        await self.repository.create(pending_doc)

        yield ProcessingProgressType(
            action="Complete",
            pending_document=pending_doc,
        )

    async def create(
        self,
        file_id: uuid.UUID,
        cluster_id: uuid.UUID,
        instructions: list[str] | None = None,
    ) -> PendingDocument:
        """Create a new pending document."""
        pending_doc = PendingDocument(
            file_id=file_id,
            cluster_id=cluster_id,
            instructions=instructions,
            status="pending",
        )
        return await self.repository.create(pending_doc)

    async def delete(self, pending_id: uuid.UUID) -> None:
        """Delete a pending document."""
        await self.repository.delete(pending_id)
```

### Lifecycle Service Pattern

**Location**: `app/graphql/{domain}/services/{entity}_lifecycle_service.py`

```python
import uuid
from enum import Enum
from app.graphql.document_processing.repositories import PendingDocumentRepository

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    STAGED = "staged"
    APPROVED = "approved"
    FAILED = "failed"

class PendingDocumentLifecycleService:
    """Manages pending document state transitions."""

    def __init__(
        self,
        pending_document_repository: PendingDocumentRepository,
    ) -> None:
        self.repository = pending_document_repository

    async def transition_to_processing(
        self,
        pending_id: uuid.UUID,
    ) -> None:
        """Transition document to processing state."""
        await self.repository.update_status(
            pending_id,
            DocumentStatus.PROCESSING.value,
        )

    async def transition_to_staged(
        self,
        pending_id: uuid.UUID,
    ) -> None:
        """Transition document to staged state."""
        await self.repository.update_status(
            pending_id,
            DocumentStatus.STAGED.value,
        )

    async def transition_to_approved(
        self,
        pending_id: uuid.UUID,
    ) -> None:
        """Transition document to approved state."""
        await self.repository.update_status(
            pending_id,
            DocumentStatus.APPROVED.value,
        )

    async def transition_to_failed(
        self,
        pending_id: uuid.UUID,
    ) -> None:
        """Transition document to failed state."""
        await self.repository.update_status(
            pending_id,
            DocumentStatus.FAILED.value,
        )
```

### Strategy Service Pattern

**Location**: `app/graphql/{domain}/services/{strategy}_strategy_service.py`

```python
from abc import ABC, abstractmethod
from app.graphql.document_processing.models import ProcessingResult

class BaseDocumentProcessingService(ABC):
    """Abstract base class for document processing strategies."""

    @abstractmethod
    async def process(
        self,
        file_info: FileInfo,
        instructions: list[str] | None,
        context: str | None,
    ) -> ProcessingResult:
        """Process a document according to the strategy."""
        pass

class PDFProcessingService(BaseDocumentProcessingService):
    """Strategy for processing PDF documents."""

    async def process(
        self,
        file_info: FileInfo,
        instructions: list[str] | None,
        context: str | None,
    ) -> ProcessingResult:
        # PDF-specific processing logic
        ...

class TabularProcessingService(BaseDocumentProcessingService):
    """Strategy for processing tabular documents (CSV, Excel)."""

    async def process(
        self,
        file_info: FileInfo,
        instructions: list[str] | None,
        context: str | None,
    ) -> ProcessingResult:
        # Tabular-specific processing logic
        ...

class DocumentProcessingStrategyService:
    """Service that returns appropriate processing strategy."""

    def __init__(
        self,
        pdf_processing_service: PDFProcessingService,
        tabular_processing_service: TabularProcessingService,
    ) -> None:
        self.pdf_service = pdf_processing_service
        self.tabular_service = tabular_processing_service

    def get_strategy(
        self,
        file_type: str,
    ) -> BaseDocumentProcessingService:
        """Get processing strategy based on file type."""
        match file_type:
            case "application/pdf":
                return self.pdf_service
            case "text/csv" | "application/vnd.ms-excel":
                return self.tabular_service
            case _:
                raise ValueError(f"Unsupported file type: {file_type}")
```

**Service Guidelines**:
- One service per domain entity or bounded context
- Inject all dependencies via constructor
- No direct database access - use repositories
- Services orchestrate business logic, not data access
- Use async/await for all I/O operations
- Use `AsyncGenerator` for streaming responses (subscriptions)
- Log important actions with `loguru.logger`
- Raise domain exceptions, not database exceptions

---

## Agent Patterns

### Agent Structure

Each AI agent follows this directory structure:

```
app/agents/{agent_name}/
├── __init__.py
├── agent.py              # Main agent class
├── models/              # Pydantic I/O models
│   ├── __init__.py
│   └── models.py
└── prompts/             # LLM prompts
    ├── __init__.py
    ├── prompt.py        # System prompt
    └── user_prompt.py   # User prompt template
```

### Agent Implementation Pattern

**Location**: `app/agents/{agent_name}/agent.py`

```python
import uuid
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from loguru import logger
from app.agents.base_agent import get_base_agent_model
from app.agents.tabular_agent.models import PythonCodeBlock
from app.agents.tabular_agent.prompts import get_tabular_agent_system_prompt
from app.core.config.settings import Settings

@dataclass
class TabularAgentDeps:
    """Dependencies injected into agent context."""
    cluster_id: uuid.UUID
    cluster_contexts: list[ClusterContext]

class TabularAgent:
    """Agent for generating Python code to transform tabular data."""

    def __init__(
        self,
        settings: Settings,
        sandbox: AsyncSandbox,
        file_info_service: FileInfoService,
    ) -> None:
        self._settings = settings
        self.sandbox = sandbox
        self.file_info_service = file_info_service
        self._agent = self._create_agent()

    def _create_agent(self) -> Agent[TabularAgentDeps, PythonCodeBlock]:
        """Create and configure the pydantic-ai agent."""
        agent = Agent(
            model=get_base_agent_model(
                self._settings,
                model_name="gpt-4o",
                temperature=0.4,
                max_tokens=8_000,
            ),
            deps_type=TabularAgentDeps,
            output_type=PythonCodeBlock,  # Structured output
            system_prompt=get_tabular_agent_system_prompt(),
            retries=2,
        )

        # Register tools the LLM can call
        _ = agent.tool(self._load_context_data)

        return agent

    async def _load_context_data(
        self,
        ctx: RunContext[TabularAgentDeps],
        context_file_names: list[str],
    ) -> str:
        """
        Tool for loading context files into the processing environment.
        The LLM can call this tool when it needs additional data.

        Args:
            ctx: Agent run context with dependencies
            context_file_names: Files to load

        Returns:
            Description of loaded data
        """
        logger.info(f"Loading context files: {context_file_names}")

        # Tool implementation
        for file_name in context_file_names:
            matching_context = next(
                (c for c in ctx.deps.cluster_contexts
                 if c.file_name.lower() == file_name.lower()),
                None,
            )

            if not matching_context:
                return f"Context file '{file_name}' not found"

            # Load and process file
            ...

        return "Successfully loaded context files"

    async def run(
        self,
        user_prompt: str,
        deps: TabularAgentDeps,
    ) -> PythonCodeBlock:
        """
        Run the agent with user prompt and dependencies.

        Args:
            user_prompt: User's transformation request
            deps: Agent dependencies

        Returns:
            Structured output (Python code block)
        """
        result = await self._agent.run(
            user_prompt=user_prompt,
            deps=deps,
        )
        return result.output
```

### Agent Model Pattern

**Location**: `app/agents/{agent_name}/models/models.py`

```python
from pydantic import BaseModel, Field
from typing import Literal

class PythonCodeBlock(BaseModel):
    """Structured output from tabular agent."""

    code: str = Field(
        ...,
        description="Python code to transform the data",
    )

    explanation: str = Field(
        ...,
        description="Explanation of what the code does",
    )

    operations: list[str] = Field(
        default_factory=list,
        description="List of operations performed (filter, join, etc.)",
    )

    execution_mode: Literal["pandas", "duckdb"] = Field(
        default="pandas",
        description="Execution engine to use",
    )

class TabularTransformationResult(BaseModel):
    """Result of tabular transformation."""

    status: Literal["success", "error"]
    output_file_url: str | None = None
    preview_data: dict | None = None
    error_message: str | None = None
```

### Agent Prompt Pattern

**Location**: `app/agents/{agent_name}/prompts/prompt.py`

```python
def get_tabular_agent_system_prompt() -> str:
    """Get system prompt for tabular agent."""
    return """
You are an expert data engineer specialized in transforming tabular data.

## Your Capabilities
- Generate Python code using Pandas or DuckDB
- Perform data transformations (filter, join, aggregate, pivot, etc.)
- Handle CSV, Excel, and Parquet files
- Access context files via the load_context_data tool

## Output Requirements
You must return a PythonCodeBlock with:
1. `code`: Valid Python code that transforms the data
2. `explanation`: Clear explanation of the transformation
3. `operations`: List of operations (e.g., ["filter", "join", "aggregate"])
4. `execution_mode`: Either "pandas" or "duckdb"

## Code Guidelines
- Use df as the input DataFrame variable
- Use result_df as the output variable
- Include error handling
- Keep code concise and readable
- Add comments for complex operations

## Example Output
```python
# Filter rows and calculate aggregates
result_df = df[df['status'] == 'active'].groupby('category')['amount'].sum()
```
""".strip()
```

**Location**: `app/agents/{agent_name}/prompts/user_prompt.py`

```python
def get_user_prompt(
    instructions: list[str],
    data_preview: str,
    context_info: str | None = None,
) -> str:
    """Generate user prompt for agent."""
    prompt = f"""
## Input Data Preview
{data_preview}

## Transformation Instructions
"""
    for i, instruction in enumerate(instructions, 1):
        prompt += f"{i}. {instruction}\n"

    if context_info:
        prompt += f"\n## Available Context Files\n{context_info}\n"

    prompt += """
Generate Python code to perform these transformations.
"""

    return prompt.strip()
```

### Base Agent Configuration

**Location**: `app/agents/base_agent.py`

```python
from pydantic_ai import Model
from app.core.config.settings import Settings

def get_base_agent_model(
    settings: Settings,
    model_name: str = "gpt-4.1-mini",
    temperature: float = 0.5,
    max_tokens: int = 4500,
) -> Model:
    """
    Get configured LLM model for agents.
    Supports both OpenAI and Anthropic models.
    """
    if model_name.startswith("claude"):
        return _get_claude_agent_model(
            settings.anthropic_api_key,
            model_name,
            temperature,
            max_tokens,
        )
    else:
        return _get_openai_agent_model(
            settings.openai_api_key,
            model_name,
            temperature,
            max_tokens,
        )

def _get_openai_agent_model(
    api_key: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
) -> Model:
    """Configure OpenAI model."""
    from pydantic_ai.models.openai import OpenAIModel

    return OpenAIModel(
        model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )

def _get_claude_agent_model(
    api_key: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
) -> Model:
    """Configure Claude model."""
    from pydantic_ai.models.anthropic import AnthropicModel

    return AnthropicModel(
        model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
```

**Agent Guidelines**:
- One agent per specialized task
- Use `pydantic-ai` for structured outputs
- Define Pydantic models for outputs
- Use dataclasses for dependencies (`deps_type`)
- Register tools with `@agent.tool` decorator
- Keep system prompts detailed and specific
- Include retry logic for robustness
- Log tool calls and agent runs

---

## Code Style Guidelines

### Python Version and Features

**Required**: Python 3.13+

Use modern Python features:

```python
# PEP 585: Use built-in generics
list[str]  # ✅ Good
List[str]  # ❌ Avoid

dict[str, Any]  # ✅ Good
Dict[str, Any]  # ❌ Avoid

# Union types with |
str | None  # ✅ Good
Optional[str]  # ❌ Avoid

int | str  # ✅ Good
Union[int, str]  # ❌ Avoid

# Walrus operator
if (match := pattern.search(text)):  # ✅ Good
    use(match)

# Structural pattern matching
match file_type:  # ✅ Good
    case "pdf":
        process_pdf()
    case "csv" | "excel":
        process_tabular()
    case _:
        raise ValueError()
```

### Type Hints

**All functions must have type hints**:

```python
# ✅ Good: Full type hints
async def get_document(
    document_id: uuid.UUID,
    include_relations: bool = False,
) -> PendingDocument | None:
    ...

# ❌ Bad: No type hints
async def get_document(document_id, include_relations=False):
    ...

# ✅ Good: Complex return types
async def process_batch(
    items: list[uuid.UUID],
) -> dict[uuid.UUID, ProcessingResult]:
    ...

# ✅ Good: Async generators
async def stream_results() -> AsyncGenerator[Result, None]:
    ...
```

### String Formatting

**Always use f-strings**:

```python
# ✅ Good
name = "Alice"
message = f"Hello, {name}!"
logger.info(f"Processing document {doc_id}")

# ❌ Bad
message = "Hello, " + name + "!"
message = "Hello, {}!".format(name)
message = "Hello, %s!" % name
```

### Path Operations

**Use pathlib.Path**:

```python
from pathlib import Path

# ✅ Good
file_path = Path("data") / "files" / "document.pdf"
if file_path.exists():
    content = file_path.read_text()

# ❌ Bad
import os
file_path = os.path.join("data", "files", "document.pdf")
if os.path.exists(file_path):
    with open(file_path) as f:
        content = f.read()
```

### Dataclasses

**Use dataclasses for data containers**:

```python
from dataclasses import dataclass

# ✅ Good: Dataclass
@dataclass
class FileInfo:
    file_id: uuid.UUID
    file_name: str
    file_size: int
    file_type: str

# ✅ Good: Frozen dataclass (immutable)
@dataclass(frozen=True)
class Config:
    api_key: str
    endpoint: str

# ❌ Bad: Manual class
class FileInfo:
    def __init__(self, file_id, file_name, file_size, file_type):
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type
```

### Enums

**Use enums for constants**:

```python
from enum import Enum

# ✅ Good
class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"

status = DocumentStatus.PENDING

# ❌ Bad
PENDING = "pending"
PROCESSING = "processing"
COMPLETE = "complete"
FAILED = "failed"
```

### Async/Await

**Prefer async/await over callbacks**:

```python
# ✅ Good: Async/await
async def process_document(doc_id: uuid.UUID) -> Result:
    file_info = await get_file_info(doc_id)
    content = await download_file(file_info.url)
    result = await process_content(content)
    return result

# ❌ Bad: Callbacks
def process_document(doc_id, callback):
    def on_file_info(file_info):
        def on_content(content):
            def on_result(result):
                callback(result)
            process_content(content, on_result)
        download_file(file_info.url, on_content)
    get_file_info(doc_id, on_file_info)
```

### Context Managers

**Use context managers for resources**:

```python
from contextlib import asynccontextmanager

# ✅ Good: Async context manager
@asynccontextmanager
async def create_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        session = AsyncSession(bind=conn)
        try:
            yield session
        finally:
            await session.close()

# Usage
async with create_session() as session:
    result = await session.execute(stmt)
```

### Error Handling

```python
# ✅ Good: Specific exceptions
from app.exceptions import DocumentNotFoundError, ProcessingError

async def get_document(doc_id: uuid.UUID) -> Document:
    document = await repository.get_by_id(doc_id)
    if not document:
        raise DocumentNotFoundError(f"Document {doc_id} not found")
    return document

# ✅ Good: Error recovery
try:
    result = await process_with_agent(data)
except AgentError as e:
    logger.error(f"Agent failed: {e}")
    result = await fallback_processing(data)

# ❌ Bad: Bare except
try:
    do_something()
except:
    pass
```

### Docstrings

**Use Google-style docstrings**:

```python
async def process_document(
    file_id: uuid.UUID,
    instructions: list[str] | None = None,
    context_files: list[uuid.UUID] | None = None,
) -> ProcessingResult:
    """
    Process a document with optional instructions and context.

    This function orchestrates the document processing pipeline,
    including file retrieval, context loading, and agent execution.

    Args:
        file_id: Unique identifier of the file to process
        instructions: Optional list of processing instructions
        context_files: Optional list of context file IDs

    Returns:
        ProcessingResult containing the processed data and metadata

    Raises:
        FileNotFoundError: If file_id doesn't exist
        ProcessingError: If processing fails

    Example:
        ```python
        result = await process_document(
            file_id=uuid.uuid4(),
            instructions=["Extract all tables"],
        )
        ```
    """
    ...
```

### Import Organization

**Order imports with isort (black profile)**:

```python
# Standard library
import asyncio
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

# Third-party packages
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from app.core.config.settings import Settings
from app.graphql.document_processing.models import PendingDocument
from app.graphql.document_processing.repositories import PendingDocumentRepository
```

### Code Formatting

**Use Ruff for linting and formatting**:

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

**Configuration**: `pyproject.toml`

```toml
[tool.ruff]
exclude = ["**/sandbox_scripts/*"]

[tool.isort]
profile = "black"
```

---

## Naming Conventions

### Files and Directories

```
# Files: snake_case
pending_document.py
document_processing_service.py
pdf_to_markdown_agent.py

# Directories: snake_case
document_processing/
pending_documents/
tabular_agent/

# Test files: test_{name}.py
test_pending_document.py
test_document_processing_service.py

# Constants file: ALL_CAPS or lowercase
constants.py
CONSTANTS.py
```

### Classes

```python
# Classes: PascalCase
class PendingDocument:
    pass

class DocumentProcessingService:
    pass

class PDFProcessingStrategy:
    pass

# Abstract classes: prefix with Base or Abstract
class BaseDocumentProcessingService(ABC):
    pass

# Type aliases: PascalCase
DocumentID = uuid.UUID
ProcessingResult = dict[str, Any]
```

### Functions and Methods

```python
# Functions: snake_case
def get_pending_document():
    pass

async def process_document():
    pass

def _internal_helper():  # Private: prefix with _
    pass

# Boolean functions: is_, has_, can_, should_
def is_valid():
    pass

def has_permissions():
    pass

async def can_process():
    pass
```

### Variables

```python
# Variables: snake_case
document_id = uuid.uuid4()
pending_documents = []
file_path = Path("data/file.pdf")

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# Private variables: prefix with _
_internal_cache = {}
_temp_data = []
```

### GraphQL Types

```python
# GraphQL types: PascalCase with Type suffix
@strawberry.type
class PendingDocumentType:
    pass

@strawberry.input
class CreatePendingDocumentInput:
    pass

@strawberry.type
class ProcessingProgressType:
    pass

# Enums: PascalCase
@strawberry.enum
class DocumentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
```

### Database Tables

```sql
-- Tables: snake_case, plural
pending_documents
document_clusters
pending_document_pages

-- Columns: snake_case
file_id
cluster_id
created_at
updated_at

-- Indexes: ix_{schema}_{table}_{column}
ix_ai_pending_documents_file_id
ix_ai_document_clusters_tenant_id

-- Foreign keys: fk_{table}_{ref_table}
fk_pending_documents_clusters
```

### Repository and Service Methods

```python
# CRUD operations
class PendingDocumentRepository:
    async def create(...) -> Model:
        pass

    async def get_by_id(...) -> Model | None:
        pass

    async def get_by_{attribute}(...) -> list[Model]:
        pass

    async def list_all(...) -> list[Model]:
        pass

    async def update(...) -> Model:
        pass

    async def delete(...) -> None:
        pass

# Service methods: verb_noun pattern
class DocumentProcessingService:
    async def process_document(...):
        pass

    async def generate_instructions(...):
        pass

    async def validate_input(...):
        pass

    async def transform_data(...):
        pass
```

---

## File Organization

### File Length Guidelines

- **Maximum file length**: 500 lines (excluding imports and docstrings)
- **Ideal function length**: 20-50 lines
- **Maximum function length**: 100 lines

**When to split files**:

```
# ✅ Good: Split large modules
app/graphql/document_processing/services/
├── pending_document_service.py          # Main service (200 lines)
├── pending_document_lifecycle_service.py  # State management (150 lines)
├── preprocessing_service.py             # Preprocessing (180 lines)
└── document_processing_orchestrator_service.py  # Orchestration (220 lines)

# ❌ Bad: Single massive file
app/graphql/document_processing/services/
└── document_service.py  # 800 lines - too large!
```

### Module Organization

**Each module should have clear purpose**:

```python
# app/graphql/document_processing/models/__init__.py
"""
Database models for document processing domain.

This module contains SQLAlchemy ORM models for:
- PendingDocument: Documents awaiting processing
- DocumentCluster: Groups of related documents
- PendingDocumentPage: Individual pages of documents
- ClusterContext: Context files for clusters
"""

from app.graphql.document_processing.models.pending_document import PendingDocument
from app.graphql.document_processing.models.document_cluster import DocumentCluster
from app.graphql.document_processing.models.pending_document_page import (
    PendingDocumentPage,
)
from app.graphql.document_processing.models.cluster_context import ClusterContext

__all__ = [
    "PendingDocument",
    "DocumentCluster",
    "PendingDocumentPage",
    "ClusterContext",
]
```

### Import Structure

**Use explicit imports in __init__.py**:

```python
# ✅ Good: Explicit imports
from app.graphql.document_processing.repositories.pending_document_repository import (
    PendingDocumentRepository,
)
from app.graphql.document_processing.repositories.document_cluster_repository import (
    DocumentClusterRepository,
)

__all__ = [
    "PendingDocumentRepository",
    "DocumentClusterRepository",
]

# ❌ Bad: Star imports
from .pending_document_repository import *
from .document_cluster_repository import *
```

### Configuration Files

**Keep configuration organized**:

```
├── .env                    # Local development (gitignored)
├── .env.dev               # Development defaults (committed)
├── .env.production        # Production template (committed)
├── pyproject.toml         # Project dependencies
├── uv.lock               # Locked dependencies
├── alembic.ini           # Alembic configuration
└── .k8s/                 # Kubernetes configs
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

---

## Dependency Injection

### Container Setup

**Location**: `app/core/container.py`

```python
import functools
import aioinject
from app.core.providers import providers

@functools.cache
def create_container() -> aioinject.Container:
    """Create and configure dependency injection container."""
    container = aioinject.Container()
    for provider in providers():
        container.register(provider)
    return container
```

### Provider Registration

**Location**: `app/core/providers.py`

```python
import aioinject
from app.core.config.settings import Settings, get_settings
from app.core.context import create_context_wrapper
from app.core.db.db_provider import providers as db_providers
from app.graphql.provider_discovery import discover_providers
import app.graphql.document_processing.repositories as doc_repos
import app.graphql.document_processing.services as doc_services

def providers() -> list[aioinject.Provider]:
    """Collect all DI providers."""
    providers_list: list[aioinject.Provider] = []

    # Settings (singleton)
    settings = get_settings(Settings)
    providers_list.append(aioinject.Object(settings))

    # Context wrapper (singleton)
    providers_list.append(aioinject.Singleton(create_context_wrapper))

    # Database providers (scoped)
    providers_list.extend(db_providers)

    # Auto-discovered repositories (scoped)
    repo_providers = discover_providers(
        doc_repos,
        class_suffix="Repository",
        aioinject_type=aioinject.Scoped,
    )
    providers_list.extend(repo_providers)

    # Auto-discovered services (scoped)
    service_providers = discover_providers(
        doc_services,
        class_suffix="Service",
        aioinject_type=aioinject.Scoped,
    )
    providers_list.extend(service_providers)

    return providers_list
```

### Auto-Discovery Pattern

**Location**: `app/graphql/provider_discovery.py`

```python
import inspect
import pkgutil
from types import ModuleType
import aioinject

def discover_providers(
    modules: list[ModuleType] | ModuleType,
    class_suffix: str = "repository",
    aioinject_type: type = aioinject.Scoped,
) -> list[aioinject.Provider]:
    """
    Auto-discover and register classes as DI providers.

    Walks module tree and finds classes ending with specified suffix.
    Automatically registers them as providers of the specified type.

    Args:
        modules: Module or list of modules to search
        class_suffix: Class name suffix to match (case-insensitive)
        aioinject_type: Provider type (Singleton, Scoped, Transient)

    Returns:
        List of configured providers
    """
    if not isinstance(modules, list):
        modules = [modules]

    providers: list[aioinject.Provider] = []

    for module in modules:
        # Walk module tree
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=module.__path__,
            prefix=module.__name__ + ".",
        ):
            # Import module
            submodule = __import__(modname, fromlist="dummy")

            # Find classes matching suffix
            for name, obj in inspect.getmembers(submodule, inspect.isclass):
                if name.lower().endswith(class_suffix.lower()):
                    provider = aioinject_type(obj)
                    providers.append(provider)

    return providers
```

### Injection in GraphQL

**Location**: `app/graphql/inject.py`

```python
from typing import TypeVar, Annotated
from aioinject.ext.strawberry import inject as base_inject

T = TypeVar("T")

# Type alias for injected dependencies
Injected = Annotated[T, "injected"]

# Re-export inject decorator
inject = base_inject
```

**Usage in Resolvers**:

```python
import strawberry
from app.graphql.inject import inject, Injected
from app.graphql.document_processing.services import PendingDocumentService

@strawberry.type
class Query:
    @strawberry.field
    @inject
    async def pending_documents(
        self,
        # Dependencies automatically injected
        pending_document_service: Injected[PendingDocumentService],
    ) -> list[PendingDocumentType]:
        documents = await pending_document_service.list_all()
        return [PendingDocumentType.from_model(doc) for doc in documents]
```

### Provider Lifetimes

```python
# Singleton: Created once per application lifetime
aioinject.Singleton(DatabaseEngine)
aioinject.Singleton(RedisClient)
aioinject.Singleton(S3Client)

# Scoped: Created once per request
aioinject.Scoped(create_session)  # New session per request
aioinject.Scoped(PendingDocumentRepository)
aioinject.Scoped(DocumentProcessingService)

# Transient: Created every time it's requested
aioinject.Transient(TemporaryFileHandler)

# Object: Pre-created instance
settings = get_settings(Settings)
aioinject.Object(settings)
```

### Context Management

**Location**: `app/core/context.py`

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass
from commons.auth import AuthInfo
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass
class ContextModel:
    """Request context data."""
    auth_info: AuthInfo
    session: AsyncSession

class Context:
    """Thread-local request context."""

    def __init__(self) -> None:
        self.auth_info: AuthInfo | None = None
        self.session: AsyncSession | None = None

    @asynccontextmanager
    async def set_context(
        cls,
        request,
        auth_service,
        controller,
    ):
        """
        Set up request context with auth and database session.

        This context manager:
        1. Verifies JWT token
        2. Creates tenant-scoped database session
        3. Makes both available to DI container
        """
        # Verify token
        auth_result = await auth_service.verify_access_token_uma(request)
        auth_info = auth_result.unwrap()

        # Create tenant session
        async with controller.scoped_session(auth_info.tenant) as session:
            yield ContextModel(auth_info=auth_info, session=session)
```

---

## Testing Guidelines

### Test Organization

```
tests/
├── unit/                          # Unit tests
│   ├── agents/
│   │   └── test_tabular_agent.py
│   ├── services/
│   │   └── test_pending_document_service.py
│   └── repositories/
│       └── test_pending_document_repository.py
│
├── integration/                   # Integration tests
│   ├── test_document_processing.py
│   └── test_graphql_api.py
│
├── e2e/                          # End-to-end tests
│   └── test_document_workflow.py
│
├── fixtures/                      # Test fixtures
│   ├── __init__.py
│   └── database.py
│
└── conftest.py                   # Pytest configuration
```

### Test Configuration

**Location**: `pyproject.toml`

```toml
[tool.pytest.ini_options]
addopts = "-p no:warnings -v -x"
asyncio_mode = "auto"
```

### Unit Test Pattern

```python
import pytest
import uuid
from app.graphql.document_processing.services import PendingDocumentService
from app.graphql.document_processing.repositories import PendingDocumentRepository
from app.graphql.document_processing.models import PendingDocument

class TestPendingDocumentService:
    """Unit tests for PendingDocumentService."""

    @pytest.fixture
    def mock_repository(self, mocker):
        """Mock repository dependency."""
        return mocker.Mock(spec=PendingDocumentRepository)

    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mocked dependencies."""
        return PendingDocumentService(
            pending_document_repository=mock_repository,
            # ... other mocked dependencies
        )

    async def test_create_pending_document(
        self,
        service,
        mock_repository,
    ):
        """Test creating a pending document."""
        # Arrange
        file_id = uuid.uuid4()
        cluster_id = uuid.uuid4()
        expected_doc = PendingDocument(
            file_id=file_id,
            cluster_id=cluster_id,
            status="pending",
        )
        mock_repository.create.return_value = expected_doc

        # Act
        result = await service.create(
            file_id=file_id,
            cluster_id=cluster_id,
        )

        # Assert
        assert result.file_id == file_id
        assert result.cluster_id == cluster_id
        assert result.status == "pending"
        mock_repository.create.assert_called_once()

    async def test_delete_pending_document(
        self,
        service,
        mock_repository,
    ):
        """Test deleting a pending document."""
        # Arrange
        pending_id = uuid.uuid4()

        # Act
        await service.delete(pending_id)

        # Assert
        mock_repository.delete.assert_called_once_with(pending_id)
```

### Integration Test Pattern

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.app import create_app

@pytest.fixture
async def app():
    """Create test application."""
    return create_app()

@pytest.fixture
async def client(app):
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    """Create test database session."""
    # Setup test database
    async with create_test_session() as session:
        yield session
        # Cleanup
        await session.rollback()

class TestDocumentProcessingAPI:
    """Integration tests for document processing API."""

    async def test_create_pending_document_graphql(
        self,
        client,
        db_session,
    ):
        """Test creating pending document via GraphQL."""
        # GraphQL mutation
        mutation = """
        mutation CreatePendingDocument($input: CreatePendingDocumentInput!) {
            document {
                createPendingDocument(input: $input) {
                    id
                    fileId
                    status
                }
            }
        }
        """

        variables = {
            "input": {
                "fileId": str(uuid.uuid4()),
                "clusterId": str(uuid.uuid4()),
            }
        }

        # Execute request
        response = await client.post(
            "/graphql",
            json={"query": mutation, "variables": variables},
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["document"]["createPendingDocument"]["status"] == "pending"
```

### Mocking Guidelines

```python
# ✅ Good: Mock at service boundaries
@pytest.fixture
def mock_file_service(mocker):
    service = mocker.Mock(spec=FileService)
    service.get_file_info.return_value = FileInfo(...)
    return service

# ✅ Good: Mock external APIs
@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("openai.ChatCompletion.create")

# ❌ Bad: Don't mock internal implementation
# Don't mock private methods or internal helpers
```

---

## Deployment

### Environment Configuration

**Development**: `.env.dev`

```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
PG_URL=postgresql+asyncpg://user:pass@localhost:5432/flowai_dev
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
REDIS_URL=redis://localhost:6379
```

**Production**: `.env.production`

```env
ENVIRONMENT=production
LOG_LEVEL=INFO
PG_URL=postgresql+asyncpg://user:pass@db:5432/flowai_prod
# ... production credentials
```

### Running Locally

```bash
# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with Gunicorn (production-like)
uv run gunicorn app.api.app:create_app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### Docker Deployment

**Dockerfile**:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run migrations and start server
CMD uv run alembic upgrade head && \
    uv run gunicorn app.api.app:create_app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### Kubernetes Deployment

**Location**: `.k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flow-py-crm
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flow-py-crm
  template:
    metadata:
      labels:
        app: flow-py-crm
    spec:
      containers:
      - name: flow-py-crm
        image: flowrms/flow-py-crm:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: PG_URL
          valueFrom:
            secretKeyRef:
              name: flow-py-crm-secrets
              key: pg-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

### Modal Serverless Jobs

**Location**: `jobs/{job_name}.py`

```python
import modal
from app.core.config.settings import Settings

app = modal.App("flow-py-crm-jobs")

# Define image with dependencies
image = modal.Image.debian_slim().pip_install_from_pyproject("pyproject.toml")

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("flow-py-crm-secrets")],
    timeout=3600,
)
async def process_large_document(file_id: str):
    """Process large documents in serverless environment."""
    settings = Settings()
    # ... processing logic
    return result
```

---

## Summary

This architecture guide documents the patterns and conventions used in Flow AI. Key takeaways:

1. **Clean Architecture**: Clear separation between layers (API, Service, Repository, Model)
2. **Type Safety**: Full type hints leveraging Python 3.13 features
3. **Dependency Injection**: All dependencies injected, no global state
4. **GraphQL First**: Strawberry GraphQL with subscriptions for real-time updates
5. **AI Integration**: Structured agent outputs via pydantic-ai
6. **Modern Python**: Async/await, pattern matching, dataclasses, enums
7. **Auto-Discovery**: Services and repositories auto-registered
8. **Multi-Tenancy**: Built-in tenant isolation

When building new features:
- Follow the domain module structure
- Use dependency injection for all dependencies
- Write full type hints
- Create unit and integration tests
- Document with Google-style docstrings
- Keep files under 500 lines
- Use modern Python 3.13 features

For questions or clarifications, refer to existing code examples in similar domains.
