import uuid
from typing import Any

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.data_exchange.services import ExchangeFileService
from app.graphql.pos.data_exchange.strawberry import (
    ExchangeFileResponse,
    SendPendingFilesResponse,
    UploadExchangeFileInput,
)


@strawberry.type
class ExchangeFileMutations:
    @strawberry.mutation()
    @inject
    async def upload_exchange_files(
        self,
        data: UploadExchangeFileInput,
        service: Injected[ExchangeFileService],
    ) -> list[ExchangeFileResponse]:
        target_org_ids = [uuid.UUID(str(org_id)) for org_id in data.target_org_ids]
        results: list[ExchangeFileResponse] = []

        for upload_file in data.files:
            file_obj: Any = upload_file
            file_content = await file_obj.read()
            file_name = file_obj.filename or "file"

            exchange_file = await service.upload_file(
                file_content=file_content,
                file_name=file_name,
                reporting_period=data.reporting_period,
                is_pos=data.is_pos,
                is_pot=data.is_pot,
                target_org_ids=target_org_ids,
            )
            results.append(ExchangeFileResponse.from_model(exchange_file))

        return results

    @strawberry.mutation()
    @inject
    async def delete_exchange_file(
        self,
        file_id: strawberry.ID,
        service: Injected[ExchangeFileService],
    ) -> bool:
        return await service.delete_file(uuid.UUID(str(file_id)))

    @strawberry.mutation()
    @inject
    async def send_pending_exchange_files(
        self,
        service: Injected[ExchangeFileService],
    ) -> SendPendingFilesResponse:
        files_sent = await service.send_pending_files()
        return SendPendingFilesResponse(success=True, files_sent=files_sent)
