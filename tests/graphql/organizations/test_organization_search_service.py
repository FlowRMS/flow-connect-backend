import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.connections.exceptions import (
    UserNotFoundError,
    UserOrganizationRequiredError,
)
from app.graphql.connections.models.enums import ConnectionStatus
from app.graphql.organizations.models import OrgType
from app.graphql.organizations.repositories.pos_contact_repository import (
    OrgPosContacts,
    PosContactData,
)
from app.graphql.organizations.services.organization_search_service import (
    OrganizationSearchService,
)


class TestOrganizationSearchService:
    @pytest.fixture
    def mock_org_search_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_pos_contact_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_connection_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_agreement_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_territory_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "workos_user_123"
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_org_search_repo: AsyncMock,
        mock_pos_contact_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        mock_agreement_service: AsyncMock,
        mock_territory_repo: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> OrganizationSearchService:
        return OrganizationSearchService(
            org_search_repository=mock_org_search_repo,
            pos_contact_repository=mock_pos_contact_repo,
            connection_service=mock_connection_service,
            agreement_service=mock_agreement_service,
            territory_repository=mock_territory_repo,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_org(org_id: uuid.UUID | None = None) -> MagicMock:
        mock_org = MagicMock()
        mock_org.id = org_id or uuid.uuid4()
        return mock_org

    @pytest.mark.asyncio
    @pytest.mark.parametrize("org_type", [OrgType.MANUFACTURER, OrgType.DISTRIBUTOR])
    async def test_search_passes_org_type_to_repository(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        org_type: OrgType,
    ) -> None:
        """Search passes the provided org_type to repository."""
        user_org_id = uuid.uuid4()
        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.search.return_value = []

        await service.search(org_type, "test")

        call_kwargs = mock_org_search_repo.search.call_args.kwargs
        assert call_kwargs.get("org_type") == org_type

    @pytest.mark.asyncio
    async def test_search_returns_empty_list_when_no_results(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Returns empty list when no organizations found."""
        user_org_id = uuid.uuid4()
        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.search.return_value = []

        result = await service.search(OrgType.MANUFACTURER, "nonexistent")

        assert result == []

    @pytest.mark.asyncio
    async def test_search_includes_pos_contacts(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_pos_contact_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Results include POS contacts for each org."""
        user_org_id = uuid.uuid4()
        org_id = uuid.uuid4()
        mock_org = self._create_mock_org(org_id)

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.search.return_value = [(mock_org, True, None, None)]
        mock_pos_contact_repo.get_pos_contacts_for_orgs.return_value = {
            org_id: OrgPosContacts(
                contacts=[
                    PosContactData(id=uuid.uuid4(), name="John", email="j@x.com")
                ],
                total_count=1,
            )
        }

        result = await service.search(OrgType.MANUFACTURER, "test")

        assert len(result) == 1
        assert result[0].pos_contacts.total_count == 1
        assert result[0].pos_contacts.contacts[0].name == "John"

    @pytest.mark.asyncio
    async def test_search_handles_org_without_pos_contacts(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_pos_contact_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Orgs without POS contacts get empty contacts list."""
        user_org_id = uuid.uuid4()
        org_id = uuid.uuid4()
        mock_org = self._create_mock_org(org_id)

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.search.return_value = [(mock_org, False, None, None)]
        mock_pos_contact_repo.get_pos_contacts_for_orgs.return_value = {}

        result = await service.search(OrgType.DISTRIBUTOR, "test")

        assert result[0].pos_contacts.total_count == 0
        assert result[0].pos_contacts.contacts == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("connection_status", "expected_status"),
        [
            (ConnectionStatus.DRAFT, ConnectionStatus.DRAFT),
            (ConnectionStatus.PENDING, ConnectionStatus.PENDING),
            (ConnectionStatus.ACCEPTED, ConnectionStatus.ACCEPTED),
            (None, None),
        ],
    )
    async def test_search_includes_connection_status_from_repository(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_pos_contact_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        connection_status: ConnectionStatus | None,
        expected_status: ConnectionStatus | None,
    ) -> None:
        """Connection status comes from repository."""
        user_org_id = uuid.uuid4()
        org_id = uuid.uuid4()
        mock_org = self._create_mock_org(org_id)

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.search.return_value = [
            (mock_org, True, connection_status, None)
        ]
        mock_pos_contact_repo.get_pos_contacts_for_orgs.return_value = {}

        result = await service.search(OrgType.MANUFACTURER, "test")

        assert result[0].connection_status is expected_status

    @pytest.mark.asyncio
    async def test_search_excludes_user_own_organization(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """User's own org is excluded via exclude_org_id parameter."""
        user_org_id = uuid.uuid4()

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.search.return_value = []

        await service.search(OrgType.MANUFACTURER, "test")

        call_kwargs = mock_org_search_repo.search.call_args.kwargs
        assert call_kwargs.get("exclude_org_id") == user_org_id

    @pytest.mark.asyncio
    async def test_search_raises_error_when_user_not_found(
        self,
        service: OrganizationSearchService,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Propagates UserNotFoundError from connection service."""
        mock_connection_service.get_user_org_and_connections.side_effect = (
            UserNotFoundError("workos_user_123")
        )

        with pytest.raises(UserNotFoundError):
            await service.search(OrgType.MANUFACTURER, "test")

    @pytest.mark.asyncio
    async def test_search_raises_error_when_user_has_no_org(
        self,
        service: OrganizationSearchService,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Propagates UserOrganizationRequiredError from connection service."""
        mock_connection_service.get_user_org_and_connections.side_effect = (
            UserOrganizationRequiredError("workos_user_123")
        )

        with pytest.raises(UserOrganizationRequiredError):
            await service.search(OrgType.DISTRIBUTOR, "test")


class TestSearchForConnections:
    @pytest.fixture
    def mock_org_search_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_pos_contact_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_connection_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_agreement_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_territory_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "workos_user_123"
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_org_search_repo: AsyncMock,
        mock_pos_contact_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        mock_agreement_service: AsyncMock,
        mock_territory_repo: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> OrganizationSearchService:
        return OrganizationSearchService(
            org_search_repository=mock_org_search_repo,
            pos_contact_repository=mock_pos_contact_repo,
            connection_service=mock_connection_service,
            agreement_service=mock_agreement_service,
            territory_repository=mock_territory_repo,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_org(
        org_id: uuid.UUID | None = None,
        org_type: str = "manufacturer",
    ) -> MagicMock:
        mock_org = MagicMock()
        mock_org.id = org_id or uuid.uuid4()
        mock_org.org_type = org_type
        return mock_org

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("user_org_type", "expected_search_type"),
        [
            ("manufacturer", OrgType.DISTRIBUTOR),
            ("distributor", OrgType.MANUFACTURER),
        ],
    )
    async def test_searches_for_opposite_org_type(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        user_org_type: str,
        expected_search_type: OrgType,
    ) -> None:
        """User searches for organizations of the opposite type."""
        user_org_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, user_org_type)

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_org_search_repo.search.return_value = []

        await service.search_for_connections("test")

        call_kwargs = mock_org_search_repo.search.call_args.kwargs
        assert call_kwargs.get("org_type") == expected_search_type

    @pytest.mark.asyncio
    async def test_passes_all_filter_parameters(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """All filter parameters are passed to search."""
        user_org_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, "manufacturer")

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_org_search_repo.search.return_value = []

        await service.search_for_connections(
            "test",
            active=False,
            flow_connect_member=True,
            connected=True,
            limit=50,
        )

        call_kwargs = mock_org_search_repo.search.call_args.kwargs
        assert call_kwargs.get("active") is False
        assert call_kwargs.get("flow_connect_member") is True
        assert call_kwargs.get("connected") is True
        assert call_kwargs.get("limit") == 50

    @pytest.mark.asyncio
    async def test_rep_firms_true_searches_for_rep_firm_orgs(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """When rep_firms=True and user is manufacturer, searches for REP_FIRM orgs."""
        user_org_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, "manufacturer")

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_org_search_repo.search.return_value = []

        await service.search_for_connections("test", rep_firms=True)

        call_kwargs = mock_org_search_repo.search.call_args.kwargs
        assert call_kwargs.get("org_type") == OrgType.REP_FIRM

    @pytest.mark.asyncio
    async def test_rep_firms_false_searches_for_distributor_orgs(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """When rep_firms=False (default), manufacturer searches for DISTRIBUTOR orgs."""
        user_org_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, "manufacturer")

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_org_search_repo.search.return_value = []

        await service.search_for_connections("test", rep_firms=False)

        call_kwargs = mock_org_search_repo.search.call_args.kwargs
        assert call_kwargs.get("org_type") == OrgType.DISTRIBUTOR

    @pytest.mark.asyncio
    async def test_rep_firms_raises_error_for_non_manufacturer(
        self,
        service: OrganizationSearchService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Non-manufacturers cannot use rep_firms=True."""
        user_org_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, "distributor")

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org

        with pytest.raises(ValueError, match="Only manufacturers can search"):
            await service.search_for_connections("test", rep_firms=True)
