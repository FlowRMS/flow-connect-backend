import contextlib
from collections.abc import AsyncIterator, Iterable
from typing import Any

import aioinject
from commons.auth import AuthInfo
from commons.db.controller import MultiTenantController
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import Settings
from app.core.db.transient_session import TransientSession


@contextlib.asynccontextmanager
async def create_session(
    controller: MultiTenantController,
    auth_info: AuthInfo,
) -> AsyncIterator[AsyncSession]:
    async with controller.scoped_session(auth_info.tenant_name) as session:
        async with session.begin():
            yield session


@contextlib.asynccontextmanager
async def create_transient_session(
    controller: MultiTenantController,
    auth_info: AuthInfo,
) -> AsyncIterator[TransientSession]:
    async with controller.transient_session(auth_info.tenant_name) as session:
        async with session.begin():
            yield session  # type: ignore[return-value]


async def create_multitenant_controller(settings: Settings) -> MultiTenantController:
    controller = MultiTenantController(
        pg_url=settings.pg_url.unicode_string(),
        app_name="Flow Py CRM App",
        echo=settings.log_level == "DEBUG",
        connect_args={
            "timeout": 5,
            "command_timeout": 90,
        },
        env=settings.environment,
    )
    await controller.load_data_sources()
    return controller


async def create_multitenant_for_migration_controller(
    pg_url: str, env: str
) -> MultiTenantController:
    controller = MultiTenantController(
        pg_url=pg_url,
        app_name="FlowAI Py CRM (Migration)",
        echo=True,
        connect_args={
            "timeout": 5,
            "command_timeout": 90,
        },
        env=env,
    )
    await controller.load_data_sources()
    return controller


providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Singleton(create_multitenant_controller),
    aioinject.Scoped(create_session),
    aioinject.Transient(create_transient_session),
]
