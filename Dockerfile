FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ARG GITHUB_TOKEN

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev cmake build-essential locales curl ca-certificates git \
    libde265-dev libx265-dev libaom-dev libdav1d-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "ssh://git@github.com/"

# Configure uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.13.7-slim as runtime

COPY --from=builder /app/.venv /app/.venv

COPY app ./app
COPY start.py ./
COPY run_migrations.py ./
COPY alembic.ini ./
COPY alembic/ ./alembic
COPY models.py ./

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:${PWD}"

CMD ["python", "start.py"]