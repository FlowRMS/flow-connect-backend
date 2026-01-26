# FlowConnect Backend

Backend API for FlowConnect application.

## Environments

| Environment | Branch | URL |
|-------------|--------|-----|
| Development | `dev` | TBD |
| Staging | `staging` | TBD |
| Production | `main` | TBD |

## Local Development

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (optional)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/FlowRMS/flow-connect-backend.git
cd flow-connect-backend
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Install dependencies:
```bash
uv sync
```

4. Run migrations:
```bash
uv run python run_migrations.py
```

5. Start the server:
```bash
uv run python start.py
```

### Using Docker

```bash
docker-compose up -d
```

## Deployment

Deployments are handled automatically via GitHub Actions:

- Push to `dev` → Deploy to Development (Render)
- Push to `staging` → Deploy to Staging (Render)
- Push to `main` → Deploy to Production (Render)

## Environment Variables

See `.env.example` for required environment variables.

## CI/CD

The CI/CD pipeline runs:
- Linting (ruff)
- Type checking (pyright)
- Tests (pytest)
- Docker build and push
- Automatic deployment based on branch
