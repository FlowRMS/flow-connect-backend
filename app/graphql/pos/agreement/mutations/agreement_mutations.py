import uuid
from typing import Any

import strawberry
from aioinject import Injected
from strawberry.file_uploads import Upload

from app.graphql.di import inject
from app.graphql.pos.agreement.services.agreement_service import AgreementService
from app.graphql.pos.agreement.strawberry.agreement_response import AgreementResponse


@strawberry.type
class AgreementMutations:
    @strawberry.mutation()
    @inject
    async def upload_agreement(
        self,
        connected_org_id: strawberry.ID,
        file: Upload,
        service: Injected[AgreementService],
    ) -> AgreementResponse:
        upload_file: Any = file
        file_content = await upload_file.read()
        agreement = await service.upload_agreement(
            connected_org_id=uuid.UUID(str(connected_org_id)),
            file_content=file_content,
            file_name=upload_file.filename or "agreement.pdf",
        )
        presigned_url = await service.get_presigned_url(agreement)
        return AgreementResponse.from_model(agreement, presigned_url)

    @strawberry.mutation()
    @inject
    async def delete_agreement(
        self,
        connected_org_id: strawberry.ID,
        service: Injected[AgreementService],
    ) -> bool:
        await service.delete_agreement(uuid.UUID(str(connected_org_id)))
        return True
