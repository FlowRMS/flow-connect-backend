import os

from ddtrace import patch
from ddtrace.llmobs import LLMObs
from loguru import logger

from app.core.config.base_settings import get_settings
from app.core.config.settings import Settings

patch(loguru=True)

settings = get_settings(Settings)

os.environ["DD_API_KEY"] = settings.datadog.api_key


if "production" in settings.environment:
    LLMObs.enable(
        ml_app=settings.datadog.service,
        api_key=settings.datadog.api_key,
        site=settings.datadog.site,
        service=settings.datadog.service,
        env=settings.environment,
    )

    os.environ["DD_PROFILING_ENABLED"] = "true"
    os.environ["DD_LOGS_INJECTION"] = "true"
    os.environ["DD_AGENT_HOST"] = settings.datadog.agent_host

    logger.info(
        f"Datadog LLMObs enabled with service: {settings.datadog.service}, environment: {settings.environment}"
    )
