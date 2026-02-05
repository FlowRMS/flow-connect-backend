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
from app.core.config.resend_settings import ResendSettings
from app.core.config.s3_settings import S3Settings
from app.core.config.settings import Settings
from app.core.config.vector_settings import VectorSettings
from app.core.config.workos_settings import WorkOSSettings
from app.core.context_wrapper import create_context_wrapper
from app.core.db import db_provider
from app.core.dto_providers import providers as dto_providers
from app.core.processors.executor import ProcessorExecutor
from app.core.vector_providers import vector_providers
from app.graphql.common.services.bulk_delete_registry_factory import (
    create_bulk_delete_registry,
)
from app.graphql.common.services.entity_lookup_registry_factory import (
    create_entity_lookup_registry,
)
from app.graphql.common.services.related_entities_registry_factory import (
    create_related_entities_registry,
)
from app.graphql.common.services.search_registry_factory import (
    create_search_strategy_registry,
)
from app.graphql.processor_providers import processor_providers
from app.graphql.repositories import repository_providers
from app.graphql.service_providers import service_providers
from app.graphql.v2.core.products.services.product_import_operations import (
    ProductImportOperations,
)
from app.graphql.v2.core.products.services.product_pricing_operations import (
    ProductPricingOperations,
)
from app.integrations.gmail.config import GmailSettings
from app.integrations.microsoft_o365.config import O365Settings
from app.webhooks.workos.providers import webhook_providers
from app.workers.document_execution.converters.providers import converter_providers
from app.workers.document_execution.executor_service import DocumentExecutorService
from app.workers.services.resend_notification_service import ResendNotificationService

modules: Iterable[Iterable[aioinject.Provider[Any]]] = [
    auth_provider.providers,
    vector_providers,
    db_provider.providers,
    s3_provider.providers,
    converter_providers,
]

settings_classes: Iterable[type[BaseSettings]] = [
    Settings,
    O365Settings,
    GmailSettings,
    S3Settings,
    WorkOSSettings,
    AdminSettings,
    ResendSettings,
    VectorSettings,
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

    for provider in webhook_providers:
        providers.append(provider)

    for provider in dto_providers:
        providers.append(provider)

    providers.append(aioinject.Scoped(ProcessorExecutor))
    providers.append(aioinject.Scoped(DocumentExecutorService))
    providers.append(aioinject.Scoped(ProductImportOperations))
    providers.append(aioinject.Scoped(ProductPricingOperations))
    providers.append(aioinject.Scoped(ResendNotificationService))
    providers.append(aioinject.Singleton(create_search_strategy_registry))
    providers.append(aioinject.Scoped(create_related_entities_registry))
    providers.append(aioinject.Scoped(create_entity_lookup_registry))
    providers.append(aioinject.Scoped(create_bulk_delete_registry))

    for settings_class in settings_classes:
        providers.append(aioinject.Object(get_settings(settings_class)))

    return providers
