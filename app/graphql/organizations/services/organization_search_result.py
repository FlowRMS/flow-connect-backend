import uuid
from dataclasses import dataclass

from app.graphql.connections.models.enums import ConnectionStatus
from app.graphql.geography.models import Subdivision
from app.graphql.organizations.models import RemoteOrg
from app.graphql.organizations.repositories.pos_contact_repository import OrgPosContacts
from app.graphql.pos.agreement.models.agreement import Agreement


@dataclass
class OrganizationSearchResult:
    org: RemoteOrg
    flow_connect_member: bool
    pos_contacts: OrgPosContacts
    connection_status: ConnectionStatus | None
    connection_id: uuid.UUID | None = None
    agreement_data: tuple[Agreement, str] | None = None
    subdivisions: list[Subdivision] | None = None
