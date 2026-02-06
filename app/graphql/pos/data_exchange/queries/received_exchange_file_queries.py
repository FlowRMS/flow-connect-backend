import uuid

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.organizations.repositories import OrganizationSearchRepository
from app.graphql.pos.data_exchange.services import ReceivedExchangeFileService
from app.graphql.pos.data_exchange.strawberry import ReceivedExchangeFileResponse


@strawberry.type
class ReceivedExchangeFileQueries:
    @strawberry.field()
    @inject
    async def received_exchange_files(
        self,
        service: Injected[ReceivedExchangeFileService],
        org_search_repository: Injected[OrganizationSearchRepository],
        period: str | None = None,
        senders: list[strawberry.ID] | None = None,
        is_pos: bool | None = None,
        is_pot: bool | None = None,
    ) -> list[ReceivedExchangeFileResponse]:
        sender_uuids: list[uuid.UUID] | None = None
        if senders:
            sender_uuids = [uuid.UUID(str(sid)) for sid in senders]

        files = await service.list_received_files(
            period=period,
            senders=sender_uuids,
            is_pos=is_pos,
            is_pot=is_pot,
        )

        if not files:
            return []

        # Resolve sender org names
        sender_org_ids = list({f.sender_org_id for f in files})
        org_names = await org_search_repository.get_names_by_ids(sender_org_ids)

        return [
            ReceivedExchangeFileResponse.from_model(
                f, sender_org_name=org_names.get(f.sender_org_id, "")
            )
            for f in files
        ]
