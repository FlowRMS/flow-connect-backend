import datetime

import strawberry

from app.graphql.pos.agreement.models.agreement import Agreement


@strawberry.type
class AgreementResponse:
    id: strawberry.ID
    connected_org_id: strawberry.ID
    file_name: str
    file_size: int
    presigned_url: str
    created_at: datetime.datetime

    @staticmethod
    def from_model(agreement: Agreement, presigned_url: str) -> "AgreementResponse":
        return AgreementResponse(
            id=strawberry.ID(str(agreement.id)),
            connected_org_id=strawberry.ID(str(agreement.connected_org_id)),
            file_name=agreement.file_name,
            file_size=agreement.file_size,
            presigned_url=presigned_url,
            created_at=agreement.created_at,
        )
