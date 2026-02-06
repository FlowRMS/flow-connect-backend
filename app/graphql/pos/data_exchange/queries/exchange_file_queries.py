import uuid

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.data_exchange.services import ExchangeFileService
from app.graphql.pos.data_exchange.strawberry import (
    ExchangeFileResponse,
    PendingFilesStatsResponse,
    SentExchangeFilesByOrgResponse,
    SentExchangeFilesByPeriodResponse,
)


@strawberry.type
class ExchangeFileQueries:
    @strawberry.field()
    @inject
    async def pending_exchange_files(
        self,
        service: Injected[ExchangeFileService],
    ) -> list[ExchangeFileResponse]:
        files = await service.list_pending_files()
        return [ExchangeFileResponse.from_model(f) for f in files]

    @strawberry.field()
    @inject
    async def pending_exchange_files_stats(
        self,
        service: Injected[ExchangeFileService],
    ) -> PendingFilesStatsResponse:
        file_count, total_rows = await service.get_pending_stats()
        return PendingFilesStatsResponse(
            file_count=file_count,
            total_rows=total_rows,
        )

    @strawberry.field()
    @inject
    async def sent_exchange_files(
        self,
        service: Injected[ExchangeFileService],
        period: str | None = None,
        organizations: list[strawberry.ID] | None = None,
        is_pos: bool | None = None,
        is_pot: bool | None = None,
    ) -> list[SentExchangeFilesByPeriodResponse]:
        org_ids: list[uuid.UUID] | None = None
        if organizations:
            org_ids = [uuid.UUID(str(org_id)) for org_id in organizations]

        groups = await service.get_sent_files_grouped(
            period=period,
            organizations=org_ids,
            is_pos=is_pos,
            is_pot=is_pot,
        )

        return [
            SentExchangeFilesByPeriodResponse(
                reporting_period=group.reporting_period,
                organizations=[
                    SentExchangeFilesByOrgResponse(
                        connected_org_id=strawberry.ID(str(org.connected_org_id)),
                        connected_org_name=org.connected_org_name,
                        files=[ExchangeFileResponse.from_model(f) for f in org.files],
                        count=org.count,
                    )
                    for org in group.organizations
                ],
            )
            for group in groups
        ]
