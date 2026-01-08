from typing import Any
from uuid import UUID

from commons.auth import AuthInfo
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisStreamBroker

from app.core.config.base_settings import get_settings
from app.core.config.settings import Settings
from app.core.db.models import configure_mappers
from app.workers.tasks.campaign_tasks import (
    CAMPAIGN_PROCESSING_CRON,
    inner_check_and_process_campaigns_task,
)
from app.workers.tasks.document_tasks import inner_execute_pending_document_task
from app.workers.tasks.pending_document_status_task import (
    PendingDocumentStatusItem,
    poll_pending_document_status,
)

configure_mappers()

settings = get_settings(Settings)

broker = RedisStreamBroker(url=settings.redis_url.unicode_string())

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.task(schedule=[{"cron": CAMPAIGN_PROCESSING_CRON}])
async def check_and_process_campaigns_task() -> dict[str, object]:
    return await inner_check_and_process_campaigns_task()


@broker.task
async def execute_pending_document_task(
    pending_document_id: UUID,
    auth_info: dict[str, Any],
) -> dict[str, object]:
    auth_info_model = AuthInfo.model_validate(auth_info)
    return await inner_execute_pending_document_task(
        pending_document_id, auth_info_model
    )


@broker.task
async def pending_document_status_email_task(
    item: PendingDocumentStatusItem,
) -> None:
    await poll_pending_document_status(item)
