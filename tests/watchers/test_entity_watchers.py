from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from commons.db.v6.crm.links.entity_type import EntityType

from app.core.processors import RepositoryEvent
from app.errors.common_errors import ConflictError, NotFoundError

if TYPE_CHECKING:
    from app.graphql.watchers.services.entity_watcher_service import (
        EntityWatcherService,
    )


class TestWatcherModuleImports:
    """Tests for watcher module imports."""

    def test_entity_watcher_repository_import(self) -> None:
        """Test EntityWatcherRepository can be imported."""
        from app.graphql.watchers.repositories.entity_watcher_repository import (
            EntityWatcherRepository,
        )

        assert EntityWatcherRepository is not None

    def test_entity_watcher_service_import(self) -> None:
        """Test EntityWatcherService can be imported."""
        from app.graphql.watchers.services.entity_watcher_service import (
            EntityWatcherService,
        )

        assert EntityWatcherService is not None

    def test_watcher_notification_processor_import(self) -> None:
        """Test WatcherNotificationProcessor can be imported."""
        from app.graphql.watchers.processors.watcher_notification_processor import (
            WatcherNotificationProcessor,
        )

        assert WatcherNotificationProcessor is not None

    def test_job_watcher_notification_processor_import(self) -> None:
        """Test JobWatcherNotificationProcessor can be imported."""
        from app.graphql.watchers.processors import JobWatcherNotificationProcessor

        assert JobWatcherNotificationProcessor is not None

    def test_task_watcher_notification_processor_import(self) -> None:
        """Test TaskWatcherNotificationProcessor can be imported."""
        from app.graphql.watchers.processors import TaskWatcherNotificationProcessor

        assert TaskWatcherNotificationProcessor is not None

    def test_quote_watcher_notification_processor_import(self) -> None:
        """Test QuoteWatcherNotificationProcessor can be imported."""
        from app.graphql.watchers.processors import QuoteWatcherNotificationProcessor

        assert QuoteWatcherNotificationProcessor is not None

    def test_order_watcher_notification_processor_import(self) -> None:
        """Test OrderWatcherNotificationProcessor can be imported."""
        from app.graphql.watchers.processors import OrderWatcherNotificationProcessor

        assert OrderWatcherNotificationProcessor is not None

    def test_pre_opportunity_watcher_notification_processor_import(self) -> None:
        """Test PreOpportunityWatcherNotificationProcessor can be imported."""
        from app.graphql.watchers.processors import (
            PreOpportunityWatcherNotificationProcessor,
        )

        assert PreOpportunityWatcherNotificationProcessor is not None


class TestEntityWatcherService:
    """Tests for EntityWatcherService business logic."""

    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        """Create a mock repository with async methods."""
        repo = MagicMock()
        repo.is_watching = AsyncMock(return_value=False)
        repo.add_watcher = AsyncMock()
        repo.remove_watcher = AsyncMock(return_value=True)
        repo.get_watcher_users = AsyncMock(return_value=[])
        return repo

    @pytest.fixture
    def service(self, mock_repository: MagicMock) -> "EntityWatcherService":
        """Create service with mocked repository."""
        from app.graphql.watchers.services.entity_watcher_service import (
            EntityWatcherService,
        )

        return EntityWatcherService(repository=mock_repository)

    @pytest.mark.asyncio
    async def test_add_watcher_success(
        self, service: "EntityWatcherService", mock_repository: MagicMock
    ) -> None:
        """Test successfully adding a watcher."""
        entity_id = uuid4()
        user_id = uuid4()

        mock_repository.is_watching.return_value = False
        mock_repository.get_watcher_users.return_value = []

        result = await service.add_watcher(EntityType.JOB, entity_id, user_id)

        mock_repository.is_watching.assert_called_once_with(
            EntityType.JOB, entity_id, user_id
        )
        mock_repository.add_watcher.assert_called_once_with(
            EntityType.JOB, entity_id, user_id
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_add_watcher_already_watching_raises_conflict(
        self, service: "EntityWatcherService", mock_repository: MagicMock
    ) -> None:
        """Test adding watcher when already watching raises ConflictError."""
        entity_id = uuid4()
        user_id = uuid4()

        mock_repository.is_watching.return_value = True

        with pytest.raises(ConflictError, match="already watching"):
            await service.add_watcher(EntityType.JOB, entity_id, user_id)

        mock_repository.add_watcher.assert_not_called()

    @pytest.mark.asyncio
    async def test_remove_watcher_success(
        self, service: "EntityWatcherService", mock_repository: MagicMock
    ) -> None:
        """Test successfully removing a watcher."""
        entity_id = uuid4()
        user_id = uuid4()

        mock_repository.remove_watcher.return_value = True
        mock_repository.get_watcher_users.return_value = []

        result = await service.remove_watcher(EntityType.TASK, entity_id, user_id)

        mock_repository.remove_watcher.assert_called_once_with(
            EntityType.TASK, entity_id, user_id
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_remove_watcher_not_found_raises_error(
        self, service: "EntityWatcherService", mock_repository: MagicMock
    ) -> None:
        """Test removing non-existent watcher raises NotFoundError."""
        entity_id = uuid4()
        user_id = uuid4()

        mock_repository.remove_watcher.return_value = False

        with pytest.raises(NotFoundError, match="Watcher"):
            await service.remove_watcher(EntityType.QUOTE, entity_id, user_id)

    @pytest.mark.asyncio
    async def test_get_watchers_returns_users(
        self, service: "EntityWatcherService", mock_repository: MagicMock
    ) -> None:
        """Test getting watchers returns list of users."""
        entity_id = uuid4()
        mock_user = MagicMock()
        mock_user.email = "test@example.com"

        mock_repository.get_watcher_users.return_value = [mock_user]

        result = await service.get_watchers(EntityType.ORDER, entity_id)

        mock_repository.get_watcher_users.assert_called_once_with(
            EntityType.ORDER, entity_id
        )
        assert len(result) == 1
        assert result[0].email == "test@example.com"


class TestWatcherNotificationProcessor:
    """Tests for WatcherNotificationProcessor."""

    def test_processor_events_property(self) -> None:
        """Test processor listens to POST_UPDATE and POST_DELETE events."""
        from app.graphql.watchers.processors import JobWatcherNotificationProcessor

        mock_session = MagicMock()
        mock_notification_service = MagicMock()
        mock_repository = MagicMock()

        processor = JobWatcherNotificationProcessor(
            session=mock_session,
            notification_service=mock_notification_service,
            watcher_repository=mock_repository,
        )

        events = processor.events

        assert RepositoryEvent.POST_UPDATE in events
        assert RepositoryEvent.POST_DELETE in events
        assert len(events) == 2

    def test_processor_entity_type_is_correct(self) -> None:
        """Test each processor has correct entity type."""
        from app.graphql.watchers.processors import (
            JobWatcherNotificationProcessor,
            OrderWatcherNotificationProcessor,
            PreOpportunityWatcherNotificationProcessor,
            QuoteWatcherNotificationProcessor,
            TaskWatcherNotificationProcessor,
        )

        mock_session = MagicMock()
        mock_notification_service = MagicMock()
        mock_repository = MagicMock()

        processors = [
            (
                JobWatcherNotificationProcessor(
                    mock_session, mock_notification_service, mock_repository
                ),
                EntityType.JOB,
            ),
            (
                TaskWatcherNotificationProcessor(
                    mock_session, mock_notification_service, mock_repository
                ),
                EntityType.TASK,
            ),
            (
                QuoteWatcherNotificationProcessor(
                    mock_session, mock_notification_service, mock_repository
                ),
                EntityType.QUOTE,
            ),
            (
                OrderWatcherNotificationProcessor(
                    mock_session, mock_notification_service, mock_repository
                ),
                EntityType.ORDER,
            ),
            (
                PreOpportunityWatcherNotificationProcessor(
                    mock_session, mock_notification_service, mock_repository
                ),
                EntityType.PRE_OPPORTUNITY,
            ),
        ]

        for processor, expected_type in processors:
            assert processor.entity_type == expected_type


class TestEntityWatcherRepository:
    """Tests for EntityWatcherRepository constructor."""

    def test_repository_accepts_auth_info(self) -> None:
        """Test repository constructor accepts auth_info parameter."""
        from app.graphql.watchers.repositories.entity_watcher_repository import (
            EntityWatcherRepository,
        )

        mock_session = MagicMock()
        mock_auth_info = MagicMock()

        repo = EntityWatcherRepository(session=mock_session, auth_info=mock_auth_info)

        assert repo.session == mock_session
        assert repo.auth_info == mock_auth_info
