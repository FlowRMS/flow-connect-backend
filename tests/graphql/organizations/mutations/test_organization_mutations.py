import uuid
from unittest.mock import  MagicMock

from app.graphql.organizations.strawberry import (
    CreateOrganizationInput,
    OrganizationLiteResponse,
)


class TestOrganizationLiteResponseFromOrmModel:
    def test_maps_org_fields_correctly(self) -> None:
        """OrganizationLiteResponse.from_orm_model maps fields correctly."""
        org_id = uuid.uuid4()
        mock_org = MagicMock()
        mock_org.id = org_id
        mock_org.name = "Test Manufacturer"
        mock_org.domain = "test.com"
        mock_org.memberships = []

        result = OrganizationLiteResponse.from_orm_model(
            mock_org,
            flow_connect_member=False,
        )

        assert str(result.id) == str(org_id)
        assert result.name == "Test Manufacturer"
        assert result.domain == "test.com"
        assert result.flow_connect_member is False
        assert result.members == 0
        assert result.pos_contacts_count == 0
        assert result.pos_contacts == []
        assert result.connection_status is None
        assert result.agreement is None

    def test_counts_active_memberships(self) -> None:
        """Counts only active memberships (deleted_at is None)."""
        mock_org = MagicMock()
        mock_org.id = uuid.uuid4()
        mock_org.name = "Test"
        mock_org.domain = "test.com"

        active_member = MagicMock()
        active_member.deleted_at = None
        deleted_member = MagicMock()
        deleted_member.deleted_at = MagicMock()  # Not None = deleted

        mock_org.memberships = [active_member, deleted_member, active_member]

        result = OrganizationLiteResponse.from_orm_model(
            mock_org,
            flow_connect_member=True,
        )

        assert result.members == 2  # Only active members counted


class TestCreateOrganizationInput:
    def test_input_structure(self) -> None:
        """CreateOrganizationInput has correct structure."""
        input_data = CreateOrganizationInput(name="Test", domain="test.com")

        assert input_data.name == "Test"
        assert input_data.domain == "test.com"
        assert input_data.contact is None

    def test_input_with_contact(self) -> None:
        """CreateOrganizationInput accepts optional contact."""
        from app.graphql.organizations.strawberry import PosContactInput

        contact = PosContactInput(email="admin@test.com")
        input_data = CreateOrganizationInput(
            name="Test", domain="test.com", contact=contact
        )

        assert input_data.contact is not None
        assert input_data.contact.email == "admin@test.com"
