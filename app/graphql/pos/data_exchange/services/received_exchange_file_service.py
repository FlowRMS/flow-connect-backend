import uuid

from commons.auth import AuthInfo
from commons.s3.service import S3Service

from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.organizations.repositories import OrganizationSearchRepository
from app.graphql.pos.data_exchange.exceptions import (
    ReceivedExchangeFileNotFoundError,
)
from app.graphql.pos.data_exchange.models import (
    ReceivedExchangeFile,
    ReceivedExchangeFileStatus,
)
from app.graphql.pos.data_exchange.repositories.received_exchange_file_repository import (
    ReceivedExchangeFileRepository,
)


class ReceivedExchangeFileService:
    def __init__(
        self,
        repository: ReceivedExchangeFileRepository,
        s3_service: S3Service,
        user_org_repository: UserOrgRepository,
        org_search_repository: OrganizationSearchRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.s3_service = s3_service
        self.user_org_repository = user_org_repository
        self.org_search_repository = org_search_repository
        self.auth_info = auth_info

    async def _get_user_org_id(self) -> uuid.UUID:
        if self.auth_info.auth_provider_id is None:
            raise ReceivedExchangeFileNotFoundError("User not authenticated")
        return await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )

    async def list_received_files(
        self,
        *,
        period: str | None = None,
        senders: list[uuid.UUID] | None = None,
        is_pos: bool | None = None,
        is_pot: bool | None = None,
    ) -> list[ReceivedExchangeFile]:
        org_id = await self._get_user_org_id()
        return await self.repository.list_for_org(
            org_id,
            period=period,
            senders=senders,
            is_pos=is_pos,
            is_pot=is_pot,
        )

    async def download_file(self, file_id: uuid.UUID) -> str:
        org_id = await self._get_user_org_id()
        file = await self.repository.get_by_id(file_id, org_id)
        if file is None:
            raise ReceivedExchangeFileNotFoundError(
                f"Received exchange file {file_id} not found"
            )

        presigned_url = await self.s3_service.generate_presigned_url(file.s3_key)
        await self.repository.update_status(
            file_id, org_id, ReceivedExchangeFileStatus.DOWNLOADED.value
        )
        return presigned_url
