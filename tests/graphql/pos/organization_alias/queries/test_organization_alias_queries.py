import uuid

import strawberry

from app.graphql.pos.organization_alias.strawberry.organization_alias_types import (
    OrganizationAliasGroupResponse,
    OrganizationAliasResponse,
)


class TestOrganizationAliasGroupResponse:
    def test_response_structure(self) -> None:
        """OrganizationAliasGroupResponse has correct structure."""
        connected_org_id = uuid.uuid4()
        alias_response = OrganizationAliasResponse(
            id=strawberry.ID(str(uuid.uuid4())),
            connected_org_id=strawberry.ID(str(connected_org_id)),
            connected_org_name="Acme Corp",
            alias="Acme",
            created_at=None,
        )

        group = OrganizationAliasGroupResponse(
            connected_org_id=strawberry.ID(str(connected_org_id)),
            connected_org_name="Acme Corp",
            aliases=[alias_response],
        )

        assert str(group.connected_org_id) == str(connected_org_id)
        assert group.connected_org_name == "Acme Corp"
        assert len(group.aliases) == 1
        assert group.aliases[0].alias == "Acme"
