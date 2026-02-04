from typing import Generic, TypeVar

from commons.db.v6 import BaseModel
from commons.db.v6.crm.links.entity_type import EntityType
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.graphql.watchers.repositories.entity_watcher_repository import (
    EntityWatcherRepository,
)
from app.workers.services.resend_notification_service import ResendNotificationService

T = TypeVar("T", bound=BaseModel)


class WatcherNotificationProcessor(BaseProcessor[T], Generic[T]):
    def __init__(
        self,
        session: AsyncSession,
        notification_service: ResendNotificationService,
        watcher_repository: EntityWatcherRepository,
        entity_type: EntityType,
        entity_name_attr: str,
    ) -> None:
        super().__init__()
        self.session = session
        self.notification_service = notification_service
        self.entity_type = entity_type
        self.entity_name_attr = entity_name_attr
        self._watcher_repository = watcher_repository

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.POST_UPDATE, RepositoryEvent.POST_DELETE]

    async def process(self, context: EntityContext[T]) -> None:
        watchers = await self._watcher_repository.get_watcher_users(
            self.entity_type,
            context.entity_id,
        )

        if not watchers:
            return

        entity_name = getattr(
            context.entity, self.entity_name_attr, str(context.entity_id)
        )
        entity_type_name = self.entity_type.name.replace("_", " ").title()

        is_delete = context.event == RepositoryEvent.POST_DELETE
        action = "Deleted" if is_delete else "Updated"

        subject = f"{entity_type_name} {action}: {entity_name}"
        html_body = self._build_notification_html(entity_type_name, entity_name, action)

        for user in watchers:
            if user.email:
                logger.info(f"Sending watcher notification to {user.email}")
                _ = self.notification_service.send_email(
                    to=user.email,
                    subject=subject,
                    html_body=html_body,
                )

    def _build_notification_html(
        self,
        entity_type_name: str,
        entity_name: str,
        action: str,
    ) -> str:
        return f"""
        <html>
        <body>
            <h2>{entity_type_name} {action}</h2>
            <p>The {entity_type_name.lower()} <strong>{entity_name}</strong> has been {action.lower()}.</p>
            <p>You are receiving this notification because you are watching this entity.</p>
        </body>
        </html>
        """
