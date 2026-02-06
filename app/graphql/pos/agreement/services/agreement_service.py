import hashlib
import io
import uuid
from typing import Any

from commons.auth import AuthInfo
from commons.s3.service import S3Service

from app.graphql.connections.models import ConnectionStatus
from app.graphql.connections.repositories.connection_repository import (
    ConnectionRepository,
)
from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.pos.agreement.exceptions import (
    AgreementNotFoundError,
    ConnectionNotAcceptedError,
    S3UploadError,
)
from app.graphql.pos.agreement.models.agreement import Agreement
from app.graphql.pos.agreement.repositories.agreement_repository import (
    AgreementRepository,
)


class AgreementService:
    def __init__(
        self,
        repository: AgreementRepository,
        s3_service: S3Service,
        connection_repository: ConnectionRepository,
        user_org_repository: UserOrgRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.s3_service = s3_service
        self.connection_repository = connection_repository
        self.user_org_repository = user_org_repository
        self.auth_info = auth_info

    async def _validate_connection_accepted(self, connected_org_id: uuid.UUID) -> None:
        if self.auth_info.auth_provider_id is None:
            raise ConnectionNotAcceptedError("User not authenticated")

        user_org_id = await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )
        connection = await self.connection_repository.get_connection_by_org_id(
            user_org_id=user_org_id,
            connected_org_id=connected_org_id,
        )
        if connection is None or connection.status != ConnectionStatus.ACCEPTED.value:
            raise ConnectionNotAcceptedError(
                f"Connection with org {connected_org_id} is not accepted"
            )

    async def upload_agreement(
        self,
        connected_org_id: uuid.UUID,
        file_content: bytes,
        file_name: str,
    ) -> Agreement:
        await self._validate_connection_accepted(connected_org_id)

        existing = await self.repository.get_by_connected_org_id(connected_org_id)
        s3_key = f"agreements/{connected_org_id}/{file_name}"

        if existing and existing.s3_key != s3_key:
            await self._delete_s3_object(existing.s3_key)

        try:
            await self.s3_service.upload(
                key=s3_key,
                file_obj=io.BytesIO(file_content),
            )
        except Exception as e:
            raise S3UploadError(f"Failed to upload file to S3: {e}") from e

        file_sha = hashlib.sha256(file_content).hexdigest()
        file_size = len(file_content)

        agreement = Agreement(
            connected_org_id=connected_org_id,
            s3_key=s3_key,
            file_name=file_name,
            file_size=file_size,
            file_sha=file_sha,
        )
        agreement.created_by_id = self.auth_info.flow_user_id

        return await self.repository.upsert(agreement)

    async def get_agreement(self, connected_org_id: uuid.UUID) -> Agreement | None:
        return await self.repository.get_by_connected_org_id(connected_org_id)

    async def get_presigned_url(self, agreement: Agreement) -> str:
        return await self.s3_service.generate_presigned_url(agreement.s3_key)

    async def _delete_s3_object(self, s3_key: str) -> None:
        """Delete an object from S3 using the underlying client."""
        get_client: Any = self.s3_service.get_client
        client_ctx: Any = await get_client()
        async with client_ctx as client:
            await client.delete_object(
                Bucket=self.s3_service.bucket_name,
                Key=self.s3_service.get_full_key(s3_key),
            )

    async def delete_agreement(self, connected_org_id: uuid.UUID) -> None:
        agreement = await self.repository.get_by_connected_org_id(connected_org_id)
        if agreement is None:
            raise AgreementNotFoundError(
                f"Agreement for org {connected_org_id} not found"
            )

        await self._delete_s3_object(agreement.s3_key)
        await self.repository.delete(connected_org_id)
