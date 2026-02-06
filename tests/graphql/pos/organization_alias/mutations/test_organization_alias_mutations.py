import uuid
from unittest.mock import MagicMock

import strawberry

from app.graphql.pos.organization_alias.strawberry.organization_alias_inputs import (
    CreateOrganizationAliasInput,
)
from app.graphql.pos.organization_alias.strawberry.organization_alias_types import (
    BulkCreateFailureResponse,
    BulkCreateOrganizationAliasesResponse,
    OrganizationAliasResponse,
)


class TestCreateOrganizationAliasInput:
    def test_input_structure(self) -> None:
        """CreateOrganizationAliasInput has correct structure."""
        input_data = CreateOrganizationAliasInput(
            connected_org_id=strawberry.ID(str(uuid.uuid4())),
            alias="Test Alias",
        )

        assert input_data.alias == "Test Alias"
        assert input_data.connected_org_id is not None


class TestOrganizationAliasResponse:
    def test_from_model_maps_fields(self) -> None:
        """OrganizationAliasResponse.from_model maps fields correctly."""
        alias_id = uuid.uuid4()
        connected_org_id = uuid.uuid4()
        mock_alias = MagicMock()
        mock_alias.id = alias_id
        mock_alias.connected_org_id = connected_org_id
        mock_alias.alias = "My Alias"
        mock_alias.created_at = MagicMock()

        result = OrganizationAliasResponse.from_model(
            mock_alias,
            connected_org_name="Acme Corp",
        )

        assert str(result.id) == str(alias_id)
        assert str(result.connected_org_id) == str(connected_org_id)
        assert result.connected_org_name == "Acme Corp"
        assert result.alias == "My Alias"


class TestBulkCreateOrganizationAliasesResponse:
    def test_response_structure(self) -> None:
        """BulkCreateOrganizationAliasesResponse has correct structure."""
        failure = BulkCreateFailureResponse(
            row_number=2,
            organization_name="Unknown Corp",
            alias="Alias",
            reason="Organization not found",
        )
        response = BulkCreateOrganizationAliasesResponse(
            inserted_count=5,
            failures=[failure],
        )

        assert response.inserted_count == 5
        assert len(response.failures) == 1
        assert response.failures[0].row_number == 2
        assert response.failures[0].reason == "Organization not found"
