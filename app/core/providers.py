import itertools
from collections.abc import Iterable
from typing import Any

import aioinject
from pydantic_settings import BaseSettings

from app.admin.config.admin_settings import AdminSettings
from app.admin.providers import admin_providers
from app.auth import auth_provider
from app.core import s3_provider
from app.core.config.base_settings import get_settings
from app.core.config.s3_settings import S3Settings
from app.core.config.settings import Settings
from app.core.config.workos_settings import WorkOSSettings
from app.core.context_wrapper import create_context_wrapper
from app.core.db import db_provider
from app.core.processors.executor import ProcessorExecutor
from app.graphql.common.services.search_registry_factory import (
    create_search_strategy_registry,
)
from app.graphql.processor_providers import processor_providers
from app.graphql.repositories import repository_providers
from app.graphql.service_providers import service_providers
from app.integrations.gmail.config import GmailSettings
from app.integrations.microsoft_o365.config import O365Settings

modules: Iterable[Iterable[aioinject.Provider[Any]]] = [
    auth_provider.providers,
    db_provider.providers,
    s3_provider.providers,
]

settings_classes: Iterable[type[BaseSettings]] = [
    Settings,
    O365Settings,
    GmailSettings,
    S3Settings,
    WorkOSSettings,
    AdminSettings,
]


def providers() -> Iterable[aioinject.Provider[Any]]:
    providers: list[aioinject.Provider[Any]] = []
    providers.append(aioinject.Singleton(create_context_wrapper))
    for provider in itertools.chain.from_iterable(modules):
        providers.append(provider)

    for provider in repository_providers:
        providers.append(provider)

    for provider in service_providers:
        providers.append(provider)

    for provider in processor_providers:
        providers.append(provider)

    for provider in admin_providers:
        providers.append(provider)

    providers.append(aioinject.Scoped(ProcessorExecutor))
    providers.append(aioinject.Singleton(create_search_strategy_registry))

    for settings_class in settings_classes:
        providers.append(aioinject.Object(get_settings(settings_class)))

    return providers
