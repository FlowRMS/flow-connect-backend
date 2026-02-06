import strawberry

from app.graphql.organizations.models import OrgType, RemoteOrg

strawberry.enum(OrgType)


@strawberry.type
class UserOrganizationResponse:
    id: strawberry.ID
    name: str
    org_type: OrgType
    domain: str | None

    @staticmethod
    def from_orm_model(org: RemoteOrg) -> "UserOrganizationResponse":
        return UserOrganizationResponse(
            id=strawberry.ID(str(org.id)),
            name=org.name,
            org_type=OrgType(org.org_type),
            domain=org.domain,
        )
