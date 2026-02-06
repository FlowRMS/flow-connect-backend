import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
import strawberry

from app.graphql.pos.data_exchange.models import (
    ReceivedExchangeFile,
    ReceivedExchangeFileStatus,
)
from app.graphql.pos.data_exchange.queries.received_exchange_file_queries import (
    ReceivedExchangeFileQueries,
)


class TestReceivedExchangeFileQueries:
    @pytest.fixture
    def mock_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_org_search_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def queries(self) -> ReceivedExchangeFileQueries:
        return ReceivedExchangeFileQueries()

    @staticmethod
    def _create_mock_file(
        org_id: uuid.UUID | None = None,
        sender_org_id: uuid.UUID | None = None,
        status: str = ReceivedExchangeFileStatus.NEW.value,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ReceivedExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id or uuid.uuid4()
        mock_file.sender_org_id = sender_org_id or uuid.uuid4()
        mock_file.s3_key = f"exchange-files/{mock_file.sender_org_id}/abc123.csv"
        mock_file.file_name = "test.csv"
        mock_file.file_size = 1024
        mock_file.file_sha = "abc123"
        mock_file.file_type = "csv"
        mock_file.row_count = 100
        mock_file.reporting_period = "2026-Q1"
        mock_file.is_pos = True
        mock_file.is_pot = False
        mock_file.status = status
        mock_file.received_at = MagicMock()
        return mock_file

    @staticmethod
    async def _call_received_exchange_files(
        queries: ReceivedExchangeFileQueries,
        service: AsyncMock,
        org_search_repository: AsyncMock,
        period: str | None = None,
        senders: list[strawberry.ID] | None = None,
        is_pos: bool | None = None,
        is_pot: bool | None = None,
    ):
        """Call the method bypassing the aioinject decorator."""
        unwrapped = queries.received_exchange_files.__wrapped__
        return await unwrapped(
            queries,
            service=service,
            org_search_repository=org_search_repository,
            period=period,
            senders=senders,
            is_pos=is_pos,
            is_pot=is_pot,
        )

    @pytest.mark.asyncio
    async def test_returns_received_files_for_user_org(
        self,
        queries: ReceivedExchangeFileQueries,
        mock_service: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Returns received files scoped to user's organization."""
        sender_org_id = uuid.uuid4()
        mock_files = [
            self._create_mock_file(sender_org_id=sender_org_id),
            self._create_mock_file(sender_org_id=sender_org_id),
        ]
        mock_service.list_received_files.return_value = mock_files
        mock_org_search_repository.get_names_by_ids.return_value = {
            sender_org_id: "Sender Org"
        }

        result = await self._call_received_exchange_files(
            queries=queries,
            service=mock_service,
            org_search_repository=mock_org_search_repository,
        )

        assert len(result) == 2
        mock_service.list_received_files.assert_called_once_with(
            period=None, senders=None, is_pos=None, is_pot=None
        )

    @pytest.mark.asyncio
    async def test_filters_by_period(
        self,
        queries: ReceivedExchangeFileQueries,
        mock_service: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Filters files by reporting period."""
        mock_service.list_received_files.return_value = []
        mock_org_search_repository.get_names_by_ids.return_value = {}

        await self._call_received_exchange_files(
            queries=queries,
            service=mock_service,
            org_search_repository=mock_org_search_repository,
            period="2026-Q1",
        )

        mock_service.list_received_files.assert_called_once_with(
            period="2026-Q1", senders=None, is_pos=None, is_pot=None
        )

    @pytest.mark.asyncio
    async def test_filters_by_senders(
        self,
        queries: ReceivedExchangeFileQueries,
        mock_service: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Filters files by sender organization IDs."""
        sender_ids = [uuid.uuid4(), uuid.uuid4()]
        mock_service.list_received_files.return_value = []
        mock_org_search_repository.get_names_by_ids.return_value = {}

        await self._call_received_exchange_files(
            queries=queries,
            service=mock_service,
            org_search_repository=mock_org_search_repository,
            senders=[strawberry.ID(str(sid)) for sid in sender_ids],
        )

        call_args = mock_service.list_received_files.call_args
        assert call_args.kwargs["senders"] == sender_ids

    @pytest.mark.asyncio
    async def test_filters_by_is_pos_and_is_pot(
        self,
        queries: ReceivedExchangeFileQueries,
        mock_service: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Filters files by is_pos and is_pot flags."""
        mock_service.list_received_files.return_value = []
        mock_org_search_repository.get_names_by_ids.return_value = {}

        await self._call_received_exchange_files(
            queries=queries,
            service=mock_service,
            org_search_repository=mock_org_search_repository,
            is_pos=True,
            is_pot=False,
        )

        mock_service.list_received_files.assert_called_once_with(
            period=None, senders=None, is_pos=True, is_pot=False
        )

    @pytest.mark.asyncio
    async def test_resolves_sender_org_names(
        self,
        queries: ReceivedExchangeFileQueries,
        mock_service: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Resolves sender organization names from IDs."""
        sender_org_id = uuid.uuid4()
        mock_files = [self._create_mock_file(sender_org_id=sender_org_id)]
        mock_service.list_received_files.return_value = mock_files
        mock_org_search_repository.get_names_by_ids.return_value = {
            sender_org_id: "Test Sender Org"
        }

        result = await self._call_received_exchange_files(
            queries=queries,
            service=mock_service,
            org_search_repository=mock_org_search_repository,
        )

        assert len(result) == 1
        assert result[0].sender_org_name == "Test Sender Org"
        mock_org_search_repository.get_names_by_ids.assert_called_once_with(
            [sender_org_id]
        )
