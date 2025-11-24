import contextlib
from collections.abc import Iterable
from typing import Any, AsyncIterator

import aioinject
from commons.auth import (
    AuthInfo,
    AuthInfoService,
    AuthProviderEnum,
    AuthService,
    KeycloakService,
    KeycloakStrategy,
)

from app.core.config.auth_settings import AuthSettings
from app.core.context_wrapper import ContextWrapper


def create_auth_service_singleton(
    auth_settings: AuthSettings,
) -> AuthService:
    keycloak_strategy = KeycloakStrategy(
        KeycloakService(
            auth_settings.auth_url,
            auth_settings.client_id,
            auth_settings.client_secret,
        )
    )
    return AuthService(
        strategies={
            AuthProviderEnum.KEYCLOAK: keycloak_strategy,
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
) -> AsyncIterator[AuthInfo]:  # pragma: no cover
    yield context_wrapper.get().auth_info


providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Singleton(create_auth_service_singleton),
    aioinject.Scoped(create_auth_info_service),
    aioinject.Scoped(create_auth_info),
]
