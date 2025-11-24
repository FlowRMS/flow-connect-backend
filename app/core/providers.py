import itertools
from collections.abc import Iterable
from typing import Any

import aioinject
from pydantic_settings import BaseSettings

from app.auth import auth_provider
from app.core.config.auth_settings import AuthSettings
from app.core.config.base_settings import get_settings
from app.core.config.settings import Settings
from app.core.context_wrapper import create_context_wrapper
from app.core.db import db_provider
from app.graphql.repositories import repository_providers
from app.graphql.service_providers import service_providers

modules: Iterable[Iterable[aioinject.Provider[Any]]] = [
    auth_provider.providers,
    db_provider.providers,
]

settings_classes: Iterable[type[BaseSettings]] = [Settings, AuthSettings]


def providers() -> Iterable[aioinject.Provider[Any]]:
    providers: list[aioinject.Provider[Any]] = []
    providers.append(aioinject.Singleton(create_context_wrapper))
    for provider in itertools.chain.from_iterable(modules):
        providers.append(provider)

    for provider in repository_providers:
        providers.append(provider)

    for provider in service_providers:
        providers.append(provider)

    for settings_class in settings_classes:
        providers.append(aioinject.Object(get_settings(settings_class)))

    return providers
