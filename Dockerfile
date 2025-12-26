FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ARG GITHUB_TOKEN
ARG COMMONS_VERSION=1.06.8

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev cmake build-essential locales curl ca-certificates git \
    libde265-dev libx265-dev libaom-dev libdav1d-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "ssh://git@github.com/"


# Configure uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy and patch pyproject.toml to use git source instead of workspace
COPY pyproject.toml uv.lock ./
RUN sed -i "s/{ workspace = true }/{ git = \"ssh:\/\/git@github.com\/FlowRMS\/flowbot-commons.git\", tag = \"${COMMONS_VERSION}\" }/" pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.13-slim as runtime

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