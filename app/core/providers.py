import itertools
from collections.abc import Iterable
from typing import Any

import aioinject
from pydantic_settings import BaseSettings

from app.auth import auth_provider
from app.core.config.base_settings import get_settings
from app.core.config.flow_connect_api_settings import FlowConnectApiSettings
from app.core.config.settings import Settings
from app.core.config.workos_settings import WorkOSSettings
from app.core.context_wrapper import create_context_wrapper
from app.core.db import db_provider, orgs_db_provider
from app.core.s3 import provider as s3_provider
from app.core.s3.settings import S3Settings
from app.graphql.di.api_client_providers import api_client_providers
from app.graphql.di.repository_providers import repository_providers
from app.graphql.di.service_providers import service_providers

modules: Iterable[Iterable[aioinject.Provider[Any]]] = [
    api_client_providers,
    auth_provider.providers,
    db_provider.providers,
    orgs_db_provider.providers,
    s3_provider.providers,
    repository_providers,
    service_providers,
]

settings_classes: Iterable[type[BaseSettings]] = [
    FlowConnectApiSettings,
    S3Settings,
    Settings,
    WorkOSSettings,
]


def providers() -> Iterable[aioinject.Provider[Any]]:
    result: list[aioinject.Provider[Any]] = [
        aioinject.Singleton(create_context_wrapper),
    ]

    for provider in itertools.chain.from_iterable(modules):
        result.append(provider)

    for settings_class in settings_classes:
        result.append(aioinject.Object(get_settings(settings_class)))

    return result
