from collections.abc import Iterable
from typing import Any

import aioinject

from app.webhooks.workos.services.user_sync_service import UserSyncService

webhook_providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Scoped(UserSyncService),
]
