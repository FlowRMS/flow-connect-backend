import contextlib
import os
import time
from typing import Any
from urllib.parse import urlparse, urlunparse

from aioinject.ext.fastapi import AioInjectMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import configure_mappers
from sqlalchemy.pool import NullPool

from app.core.config.base_settings import get_settings
from app.core.config.settings import Settings
from app.core.config.workos_settings import WorkOSSettings
from app.core.container import create_container
from app.graphql.app import create_graphql_app
from app.tenant_provisioning.database_service import DatabaseCreationService
from app.tenant_provisioning.migration_service import MigrationService
from app.tenant_provisioning.repository import TenantRepository
from app.tenant_provisioning.service import (
    ProvisioningResult,
    TenantProvisioningService,
)
from app.webhooks.workos.router import create_workos_webhook_router


class SessionScopedProvisioningService:
    """Wrapper that creates a new session for each provisioning call."""

    session_factory: async_sessionmaker[AsyncSession]
    database_service: DatabaseCreationService
    migration_service: MigrationService
    db_connection_url: str
    db_host: str
    db_ro_host: str
    db_username: str

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        database_service: DatabaseCreationService,
        migration_service: MigrationService,
        db_connection_url: str,
        db_host: str,
        db_ro_host: str,
        db_username: str,
    ) -> None:
        self.session_factory = session_factory
        self.database_service = database_service
        self.migration_service = migration_service
        self.db_connection_url = db_connection_url
        self.db_host = db_host
        self.db_ro_host = db_ro_host
        self.db_username = db_username

    async def provision(self, org_id: str, org_name: str) -> ProvisioningResult:
        async with self.session_factory() as session:
            async with session.begin():
                repository = TenantRepository(session)
                service = TenantProvisioningService(
                    repository=repository,
                    database_service=self.database_service,
                    migration_service=self.migration_service,
                    db_connection_url=self.db_connection_url,
                    db_host=self.db_host,
                    db_ro_host=self.db_ro_host,
                    db_username=self.db_username,
                )
                return await service.provision(org_id, org_name)


def create_app() -> FastAPI:
    container = create_container()
    settings = get_settings(Settings)
    workos_settings = get_settings(WorkOSSettings)

    # Create public schema engine for tenant provisioning
    pg_url = settings.pg_url.unicode_string()
    public_engine = create_async_engine(
        pg_url,
        poolclass=NullPool,
        echo=settings.log_level == "DEBUG",
    )
    public_session_factory = async_sessionmaker(
        bind=public_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Parse URL to extract components for tenant records
    # Convert to sync SQLAlchemy format for migrations (remove +asyncpg)
    sync_pg_url = pg_url.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(sync_pg_url)

    # Extract hostname and username from URL
    db_host = parsed.hostname or ""
    db_username = parsed.username or ""

    # Read-only host from settings, fallback to main host
    db_ro_host = settings.pg_ro_host or db_host

    # Build connection URL base (without database name) for migrations
    db_connection_url = urlunparse(parsed._replace(path=""))

    # Create provisioning services
    database_service = DatabaseCreationService(pg_url)
    migration_service = MigrationService()
    provisioning_service = SessionScopedProvisioningService(
        session_factory=public_session_factory,
        database_service=database_service,
        migration_service=migration_service,
        db_connection_url=db_connection_url,
        db_host=db_host,
        db_ro_host=db_ro_host,
        db_username=db_username,
    )

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        configure_mappers()
        async with container:
            try:
                yield
            finally:
                await public_engine.dispose()
                logger.info("Application shutdown")

    app = FastAPI(
        title="Flow Connect API",
        description="Flow Connect Backend API built with FastAPI and Strawberry GraphQL",
        version="0.0.1",
        lifespan=lifespan,
        openapi_url=None,
    )

    app.add_middleware(AioInjectMiddleware, container=container)
    app.include_router(create_graphql_app(), prefix="/graphql")

    # Register WorkOS webhook router
    if workos_settings.workos_webhook_secret:
        webhook_router = create_workos_webhook_router(
            workos_settings.workos_webhook_secret,
            provisioning_service=provisioning_service,  # pyright: ignore[reportArgumentType]
        )
        app.include_router(webhook_router)
        logger.info("WorkOS webhook router registered")

    cors_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    extra_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    if extra_origins:
        cors_origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Any) -> JSONResponse:  # pyright: ignore[reportUnusedFunction]
        try:
            start_time = time.perf_counter()
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            process_time = round(process_time * 1000, 2)
            response.headers["X-Process-Time-Ms"] = f"{process_time}ms"
        except Exception:
            import traceback

            return JSONResponse(
                status_code=500, content={"detail": traceback.format_exc()}
            )

        return response

    @app.get("/api/health", include_in_schema=True)
    def health_check():  # pyright: ignore[reportUnusedFunction]
        return {"status": "ok"}

    return app
