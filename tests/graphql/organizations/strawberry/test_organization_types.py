import uuid
from datetime import datetime, timezone

import pytest

from app.graphql.organizations.models import RemoteOrg
from app.graphql.organizations.strawberry import OrganizationLiteResponse


class TestOrganizationLiteResponse:
    def test_from_orm_model_with_na_name_uses_domain_fallback(self) -> None:
        """When org.name is '#N/A', should use domain as fallback."""
        org = RemoteOrg(
            id=uuid.uuid4(),
            name="#N/A",
            domain="cpsreps.com",
            org_type="rep_firm",
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            deleted_at=None,
        )
        # Mock the memberships relationship
        org.memberships = []

        response = OrganizationLiteResponse.from_orm_model(
            org, flow_connect_member=False
        )

        # Should use domain instead of "#N/A"
        assert response.name == "cpsreps.com"

    def test_from_orm_model_with_valid_name_uses_name(self) -> None:
        """When org.name is valid, should use the name as-is."""
        org = RemoteOrg(
            id=uuid.uuid4(),
            name="CPS Representatives",
            domain="cpsreps.com",
            org_type="rep_firm",
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            deleted_at=None,
        )
        org.memberships = []

        response = OrganizationLiteResponse.from_orm_model(
            org, flow_connect_member=False
        )

        assert response.name == "CPS Representatives"

    def test_from_orm_model_with_na_name_and_no_domain_uses_na(self) -> None:
        """When org.name is '#N/A' and domain is None, should keep '#N/A'."""
        org = RemoteOrg(
            id=uuid.uuid4(),
            name="#N/A",
            domain=None,
            org_type="rep_firm",
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            deleted_at=None,
        )
        org.memberships = []

        response = OrganizationLiteResponse.from_orm_model(
            org, flow_connect_member=False
        )

        # If no domain available, keep the original name
        assert response.name == "#N/A"
