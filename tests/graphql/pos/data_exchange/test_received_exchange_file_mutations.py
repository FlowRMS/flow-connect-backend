import uuid
from unittest.mock import AsyncMock

import pytest
import strawberry

from app.graphql.pos.data_exchange.mutations.received_exchange_file_mutations import (
    ReceivedExchangeFileMutations,
)


class TestReceivedExchangeFileMutations:
    @pytest.fixture
    def mock_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mutations(self) -> ReceivedExchangeFileMutations:
        return ReceivedExchangeFileMutations()

    @staticmethod
    async def _call_download_received_exchange_file(
        mutations: ReceivedExchangeFileMutations,
        service: AsyncMock,
        file_id: strawberry.ID,
    ):
        """Call the method bypassing the aioinject decorator."""
        unwrapped = mutations.download_received_exchange_file.__wrapped__
        return await unwrapped(
            mutations,
            service=service,
            file_id=file_id,
        )

    @pytest.mark.asyncio
    async def test_returns_presigned_url(
        self,
        mutations: ReceivedExchangeFileMutations,
        mock_service: AsyncMock,
    ) -> None:
        """Returns presigned URL for file download."""
        file_id = uuid.uuid4()
        expected_url = "https://s3.example.com/presigned-url"
        mock_service.download_file.return_value = expected_url

        result = await self._call_download_received_exchange_file(
            mutations=mutations,
            service=mock_service,
            file_id=strawberry.ID(str(file_id)),
        )

        assert result.url == expected_url
        mock_service.download_file.assert_called_once_with(file_id)

    @pytest.mark.asyncio
    async def test_converts_strawberry_id_to_uuid(
        self,
        mutations: ReceivedExchangeFileMutations,
        mock_service: AsyncMock,
    ) -> None:
        """Converts strawberry.ID to UUID for service call."""
        file_id = uuid.uuid4()
        mock_service.download_file.return_value = "https://example.com"

        await self._call_download_received_exchange_file(
            mutations=mutations,
            service=mock_service,
            file_id=strawberry.ID(str(file_id)),
        )

        # Verify the service received a UUID, not a string
        call_args = mock_service.download_file.call_args
        assert call_args.args[0] == file_id
        assert isinstance(call_args.args[0], uuid.UUID)
