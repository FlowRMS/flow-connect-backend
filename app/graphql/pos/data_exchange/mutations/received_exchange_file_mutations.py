import uuid

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.data_exchange.services import ReceivedExchangeFileService
from app.graphql.pos.data_exchange.strawberry import DownloadReceivedFileResponse


@strawberry.type
class ReceivedExchangeFileMutations:
    @strawberry.mutation()
    @inject
    async def download_received_exchange_file(
        self,
        file_id: strawberry.ID,
        service: Injected[ReceivedExchangeFileService],
    ) -> DownloadReceivedFileResponse:
        url = await service.download_file(uuid.UUID(str(file_id)))
        return DownloadReceivedFileResponse(url=url)
