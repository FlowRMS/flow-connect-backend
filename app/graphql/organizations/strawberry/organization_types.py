import strawberry

from app.graphql.connections.models.enums import ConnectionStatus
from app.graphql.geography.strawberry.geography_types import SubdivisionResponse
from app.graphql.organizations.models import RemoteOrg
from app.graphql.organizations.repositories.pos_contact_repository import (
    OrgPosContacts,
    PosContactData,
)
from app.graphql.pos.agreement.models.agreement import Agreement
from app.graphql.pos.agreement.strawberry.agreement_response import AgreementResponse

# Register ConnectionStatus with strawberry (must be done before use in type annotations)
strawberry.enum(ConnectionStatus)


@strawberry.type
class PosContact:
    id: strawberry.ID
    name: str | None
    email: str | None

    @staticmethod
    def from_data(data: PosContactData) -> "PosContact":
        return PosContact(
            id=strawberry.ID(str(data.id)),
            name=data.name,
            email=data.email,
        )


@strawberry.type
class OrganizationLiteResponse:
    id: strawberry.ID
    name: str
    domain: str | None
    members: int
    pos_contacts_count: int
    pos_contacts: list[PosContact]
    flow_connect_member: bool
    connection_status: ConnectionStatus | None
    agreement: AgreementResponse | None
    subdivisions: list[SubdivisionResponse]

    @staticmethod
    def from_orm_model(
        org: RemoteOrg,
        *,
        flow_connect_member: bool,
        pos_contacts: OrgPosContacts | None = None,
        connection_status: ConnectionStatus | None = None,
        agreement_data: tuple[Agreement, str] | None = None,
        subdivisions: list[SubdivisionResponse] | None = None,
    ) -> "OrganizationLiteResponse":
        contacts_data = pos_contacts or OrgPosContacts(contacts=[], total_count=0)
        agreement = None
        if agreement_data is not None:
            agreement_model, presigned_url = agreement_data
            agreement = AgreementResponse.from_model(agreement_model, presigned_url)

        # Fallback: if name is "#N/A" (from bad CSV import), use domain instead
        display_name = org.domain if org.name == "#N/A" and org.domain else org.name

        return OrganizationLiteResponse(
            id=strawberry.ID(str(org.id)),
            name=display_name,
            domain=org.domain,
            members=len([m for m in org.memberships if m.deleted_at is None]),
            pos_contacts_count=contacts_data.total_count,
            pos_contacts=[PosContact.from_data(c) for c in contacts_data.contacts],
            flow_connect_member=flow_connect_member,
            connection_status=connection_status,
            agreement=agreement,
            subdivisions=subdivisions or [],
        )
