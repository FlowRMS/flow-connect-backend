# Flow Py CRM

A modern, multi-tenant CRM backend built with Python 3.13, FastAPI, and Strawberry GraphQL. This service provides a comprehensive GraphQL API for managing customer relationships, jobs, quotes, orders, invoices, and more.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Migrations](#database-migrations)
- [Development](#development)
- [Docker](#docker)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)

---

## Features

- **GraphQL API** with Strawberry GraphQL for type-safe queries and mutations
- **Multi-tenancy** with built-in tenant isolation and schema separation
- **Microsoft 365 Integration** - Email and calendar sync via O365
- **Gmail Integration** - Email sync via Google Gmail API
- **Async Architecture** - Built on FastAPI and SQLAlchemy async for high performance
- **Dependency Injection** - Uses `aioinject` for clean, testable architecture
- **Type Safety** - Full type hints using Python 3.13 modern typing features
- **JWT Authentication** - Secure authentication with Keycloak/OpenID Connect

---

## Prerequisites

- **Python 3.13+**
- **UV** (Python package manager) - [Install UV](https://docs.astral.sh/uv/getting-started/installation/)
- **PostgreSQL 15+**
- **Docker** (optional, for containerized deployment)
- **Task** (optional, task runner) - [Install Task](https://taskfile.dev/)

### Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/FlowRMS/flow-py-crm.git
cd flow-py-crm
```

### 2. Install Dependencies

```bash
# Install all dependencies (including dev dependencies)
uv sync

# Install production dependencies only
uv sync --no-dev
```

### 3. Set Up Environment Variables

Copy an environment file and configure it:

```bash
cp .env.staging .env.local
```

Edit `.env.local` with your configuration (see [Configuration](#configuration) section).

---

## Configuration

### Environment Variables

Create a `.env.local` file (or `.env.dev`, `.env.staging`, `.env.prod`) with the following variables:

```env
# Application
ENVIRONMENT=local
LOG_LEVEL=DEBUG

# Database
PG_URL=postgresql+asyncpg://postgres:password@localhost:5432/flowcrm

# Authentication
AUTH_URL=https://your-auth-server.com/realms/admin/protocol/openid-connect/token
CLIENT_ID=AI
CLIENT_SECRET=your-client-secret

# Microsoft 365 Integration (Optional)
O365_CLIENT_ID=your-o365-client-id
O365_CLIENT_SECRET=your-o365-client-secret
O365_REDIRECT_URI=http://localhost:3000/integrations/o365/callback

# Gmail Integration (Optional)
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:8000/api/integrations/gmail/callback

# Server Configuration (Production)
HOST=0.0.0.0
PORT=5555
MAX_NUMBER_OF_WORKERS=5
KEEP_ALIVE=5
GRACEFUL_TIMEOUT=120
ACCESS_LOG=-
```

### Private PyPI Configuration

Set up authentication for the FlowRMS private PyPI repository:

```bash
# Set credentials in environment
export UV_INDEX_flowrms_USERNAME=flowbot-user
export UV_INDEX_flowrms_PASSWORD=your-token-here

# Or configure in .netrc
echo "machine pypi.flowrms.com login flowbot-user password your-token" >> ~/.netrc
```

---

## Running the Application

### Development Mode

```bash
# Run with hot reload (port 8006)
uv run python main.py

# Or specify environment
uv run python main.py --env dev
uv run python main.py --env staging
```

### Production Mode

```bash
# Run with Uvicorn multi-worker (port 5555 by default)
uv run python start.py
```

### Environment Variables for Production

```bash
export HOST=0.0.0.0
export PORT=5555
export LOG_LEVEL=info
export MAX_NUMBER_OF_WORKERS=5
export KEEP_ALIVE=5
export GRACEFUL_TIMEOUT=120
```

### Accessing the API

- **GraphQL Playground**: http://localhost:8006/graphql (development) or http://localhost:5555/graphql (production)
- **Health Check**: http://localhost:8006/api/health

---

## Database Migrations

### Run Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Check current migration status
uv run alembic current

# View migration history
uv run alembic history
```

### Multi-Tenant Migrations

For multi-tenant deployments, use the migration runner:

```bash
uv run python run_migrations.py
```

### Create New Migration

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "description_of_changes"

# Create empty migration
uv run alembic revision -m "description_of_changes"
```

### Rollback Migration

```bash
# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>
```

---

## Development

### Code Quality

```bash
# Run all checks (lint + typecheck)
task all

# Run linting only (Ruff format + import sorting)
task lint

# Run type checking with basedpyright (recommended)
task typecheck-basedpy

# Run type checking with mypy
task typecheck

# Export GraphQL schema
task gql
```

### Available Task Commands

| Task | Description |
|------|-------------|
| `task all` | Run lint + typecheck-basedpy |
| `task lint` | Format and lint code with Ruff |
| `task typecheck` | Type check with mypy |
| `task typecheck-basedpy` | Type check with basedpyright |
| `task gql` | Export GraphQL schema to schema.graphql |
| `task lints` | Run lint + typecheck-basedpy |

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_example.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=app
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

---

## Docker

### Build and Run with Docker Compose

```bash
# Build and start services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f crm

# Stop services
docker-compose down
```

### Build Docker Image Manually

```bash
# Build with private package index
docker build \
  --build-arg GITHUB_TOKEN=GITHUB_TOKEN \
  -t flow-py-crm:latest .

# Run container
docker run -p 8000:8000 --env-file .env.staging flow-py-crm:latest
```

---

## API Documentation

### GraphQL Endpoint

The GraphQL API is available at `/graphql`. Use the GraphQL Playground for interactive exploration.

### CRM Entities

The API provides full CRUD operations for:

- **Companies** - Organization management with addresses
- **Contacts** - Contact information and relationships
- **Customers** - Customer records and history
- **Jobs** - Job tracking and management
- **Pre-Opportunities** - Sales pipeline pre-opportunities
- **Quotes** - Quote generation and management
- **Orders** - Order processing
- **Invoices** - Invoice management
- **Checks** - Payment tracking
- **Tasks** - Task management with reminders
- **Notes** - Notes and conversation threads
- **Campaigns** - Marketing campaign tracking
- **Links** - Related resource links

### Example Queries

```graphql
# Get a job by ID
query GetJob($id: ID!) {
  job {
    get(id: $id) {
      id
      jobNumber
      status
      customer {
        name
      }
      quotes {
        id
        totalAmount
      }
    }
  }
}

# List contacts
query ListContacts($filters: ContactFilterInput) {
  contact {
    list(filters: $filters) {
      items {
        id
        firstName
        lastName
        email
        company {
          name
        }
      }
      totalCount
    }
  }
}
```

### Example Mutations

```graphql
# Create a new contact
mutation CreateContact($input: CreateContactInput!) {
  contact {
    create(input: $input) {
      id
      firstName
      lastName
      email
    }
  }
}

# Update a job status
mutation UpdateJob($id: ID!, $input: UpdateJobInput!) {
  job {
    update(id: $id, input: $input) {
      id
      status
      updatedAt
    }
  }
}
```

### Authentication

All API requests require a valid JWT token in the Authorization header:

```bash
curl -X POST http://localhost:8006/graphql \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ job { list { items { id jobNumber } } } }"}'
```

---

## Architecture

### Key Technologies

| Category | Technology |
|----------|------------|
| Web Framework | FastAPI |
| GraphQL | Strawberry GraphQL |
| ORM | SQLAlchemy 2.0 (async) |
| Database Driver | asyncpg |
| Database | PostgreSQL |
| Migrations | Alembic |
| DI Container | aioinject |
| Auth | JWT + Keycloak |
| Package Manager | UV |
| Linting | Ruff |
| Type Checking | basedpyright |

### Multi-Tenant Architecture

- Uses schema-based tenant isolation
- `MultiTenantController` from flowbot-commons
- Automatic tenant context injection via middleware
- Separate alembic version tracking per schema

### Dependency Injection

The application uses `aioinject` for dependency injection:

```python
# Services are automatically injected into GraphQL resolvers
@strawberry.type
class JobQueries:
    @strawberry.field
    async def get(self, id: ID, job_service: JobService) -> Job:
        return await job_service.get_by_id(id)
```

For detailed architecture documentation, see [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md).

---

## Integrations

### Microsoft 365

Configure O365 integration for email and calendar sync:

1. Set up Azure AD application with appropriate permissions
2. Configure environment variables (`O365_CLIENT_ID`, `O365_CLIENT_SECRET`, `O365_REDIRECT_URI`)
3. OAuth callback endpoint: `/api/integrations/o365/callback`

### Gmail

Configure Gmail integration for email sync:

1. Set up Google Cloud project with Gmail API enabled
2. Configure environment variables (`GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REDIRECT_URI`)
3. OAuth callback endpoint: `/api/integrations/gmail/callback`

---

## Troubleshooting

### Common Issues

**UV package installation fails with private index:**

```bash
# Set credentials for private package index
export UV_INDEX_flowrms_USERNAME=flowbot-user
export UV_INDEX_flowrms_PASSWORD=your-password
uv sync
```

**Database connection issues:**

```bash
# Ensure PostgreSQL is running
pg_isready -h localhost -p 5432

# Check connection string format
# postgresql+asyncpg://user:password@host:port/database
```

**Port already in use:**

```bash
# Find process using the port
lsof -i :8006

# Kill the process
kill -9 <PID>
```

**Alembic migration errors:**

```bash
# Check current state
uv run alembic current

# Stamp to a specific version if needed
uv run alembic stamp <revision_id>
```

---

## Contributing

1. Create a feature branch from `staging`
2. Make your changes following the code style guidelines in [CLAUDE.md](./CLAUDE.md)
3. Run `task all` to ensure all checks pass
4. Submit a pull request to `staging`

---

## License

Proprietary - FlowRMS
