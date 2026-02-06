# Flow Connect

GraphQL FastAPI backend built with Python 3.13, Strawberry GraphQL, and WorkOS authentication.

## Prerequisites

- Python 3.13+
- UV (package manager)
- PostgreSQL

## Installation

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.dev .env.local
# Edit .env.local with your credentials
```

## Running

```bash
# Development (port 8006)
uv run python main.py --env dev

# Production (port 5555)
uv run python start.py
```

## Endpoints

- GraphQL: `http://localhost:8006/graphql`
- Health: `http://localhost:8006/api/health`

## Database Migrations

This project uses a multi-tenant architecture where each tenant has its own PostgreSQL database. Migrations are applied to all tenant databases automatically.

### Schema Isolation

**Important**: Tenant databases are shared with `flow-py-backend`. To avoid migration conflicts, each application tracks migrations in a separate schema:

| Application | Version Table | Feature Schemas |
|-------------|---------------|-----------------|
| flow-py-backend | `public.alembic_version` | `public.*` |
| flow-py-connect | `connect.alembic_version` | `connect_pos`, `connect_*` |

This isolation is configured in `alembic.ini`:
```ini
version_table_schema = connect
version_table = alembic_version
```

### Commands

```bash
# Run multi-tenant migrations (applies to all tenant databases)
uv run python run_migrations.py --env dev
uv run python run_migrations.py --env staging
uv run python run_migrations.py --env prod

# Create new migration
uv run alembic revision --autogenerate -m "description"
```

### How Multi-Tenant Migrations Work

1. Loads all active tenants from the central `tenants` table
2. For each tenant, compares `alembic_version` against current head
3. Runs pending migrations on tenants that are behind
4. Updates each tenant's `alembic_version` after success
5. Processes tenants in parallel (chunks of 2)

## Project Structure

```
flow-py-connect/
├── app/
│   ├── api/          # FastAPI app
│   ├── auth/         # WorkOS authentication
│   ├── core/         # Config, DI, middleware
│   ├── errors/       # Error handling
│   └── graphql/      # GraphQL schema & resolvers
├── alembic/          # Database migrations
├── main.py           # Dev entry point
├── start.py          # Prod entry point
└── pyproject.toml    # Dependencies
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| GraphQL | Strawberry |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL |
| Auth | WorkOS |
| DI | aioinject |
| Package Manager | UV |
