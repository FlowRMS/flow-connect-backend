import contextlib
from collections.abc import Iterable
from typing import Any, AsyncIterator

import aioinject
from commons.auth import (
    AuthInfo,
    AuthInfoService,
    AuthProviderEnum,
    AuthService,
    WorkOSStrategy,
)

from app.auth.workos_service import FlowConnectWorkOSService
from app.core.config.workos_settings import WorkOSSettings
from app.core.context_wrapper import ContextWrapper


def create_auth_service_singleton(
    workos_settings: WorkOSSettings,
) -> AuthService:
    workos_strategy = WorkOSStrategy(
        FlowConnectWorkOSService(
            api_key=workos_settings.workos_api_key,
            client_id=workos_settings.workos_client_id,
        )
    )
    return AuthService(
        strategies={
            AuthProviderEnum.WORKOS: workos_strategy,
        }
    )


def create_auth_info_service(
    auth_info: AuthInfo,
    auth_service: AuthService,
) -> AuthInfoService:
    return AuthInfoService(
        auth_info, auth_service.get_strategy_from_auth_info(auth_info)
    )


@contextlib.asynccontextmanager
async def create_auth_info(
    context_wrapper: ContextWrapper,
) -> AsyncIterator[AuthInfo]:
    yield context_wrapper.get().auth_info


providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Singleton(create_auth_service_singleton),
    aioinject.Scoped(create_auth_info_service),
    aioinject.Scoped(create_auth_info),
]
