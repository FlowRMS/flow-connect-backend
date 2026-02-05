from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from commons.auth import AuthInfo
from commons.db.v6.crm.contact_model import Contact
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.contacts.repositories.contacts_repository import ContactsRepository
from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_input import ContactInput
from app.graphql.links.services.links_service import LinksService
from app.graphql.v2.core.customers.services.customer_service import CustomerService


@pytest.fixture
def mock_auth_info() -> AuthInfo:
    """Create a mock AuthInfo object."""
    return MagicMock(spec=AuthInfo)


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Create a mock ContactsRepository."""
    repo = AsyncMock(spec=ContactsRepository)
    return repo


@pytest.fixture
def mock_link_service() -> AsyncMock:
    """Create a mock LinksService."""
    return AsyncMock(spec=LinksService)


@pytest.fixture
def mock_companies_service() -> AsyncMock:
    """Create a mock CompaniesService."""
    return AsyncMock(spec=CompaniesService)


@pytest.fixture
def mock_customer_service() -> AsyncMock:
    """Create a mock CustomerService."""
    return AsyncMock(spec=CustomerService)


@pytest.fixture
def contacts_service(
    mock_repository: AsyncMock,
    mock_auth_info: AuthInfo,
    mock_link_service: AsyncMock,
    mock_companies_service: AsyncMock,
    mock_customer_service: AsyncMock,
) -> ContactsService:
    """Create a ContactsService with mocked dependencies."""
    return ContactsService(
        repository=mock_repository,
        auth_info=mock_auth_info,
        link_service=mock_link_service,
        companies_service=mock_companies_service,
        customer_service=mock_customer_service,
    )


class TestCreateContactWithCustomerId:
    """Tests for create_contact with customer_id parameter."""

    @pytest.mark.asyncio
    async def test_create_contact_with_customer_id_creates_link(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
        mock_link_service: AsyncMock,
    ) -> None:
        """Test that creating a contact with customer_id creates a link."""
        contact_id = uuid4()
        customer_id = uuid4()

        mock_contact = MagicMock(spec=Contact)
        mock_contact.id = contact_id
        mock_repository.create.return_value = mock_contact

        contact_input = ContactInput(
            first_name="John",
            last_name="Doe",
            customer_id=customer_id,
        )

        result = await contacts_service.create_contact(contact_input)

        assert result == mock_contact
        mock_repository.create.assert_called_once()
        mock_link_service.create_link.assert_called_once_with(
            source_type=EntityType.CONTACT,
            source_id=contact_id,
            target_type=EntityType.CUSTOMER,
            target_id=customer_id,
        )

    @pytest.mark.asyncio
    async def test_create_contact_with_both_company_and_customer_creates_both_links(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
        mock_link_service: AsyncMock,
    ) -> None:
        """Test that creating a contact with both company_id and customer_id creates both links."""
        contact_id = uuid4()
        company_id = uuid4()
        customer_id = uuid4()

        mock_contact = MagicMock(spec=Contact)
        mock_contact.id = contact_id
        mock_repository.create.return_value = mock_contact

        contact_input = ContactInput(
            first_name="Jane",
            last_name="Smith",
            company_id=company_id,
            customer_id=customer_id,
        )

        _ = await contacts_service.create_contact(contact_input)

        assert mock_link_service.create_link.call_count == 2


class TestCreateContactWithoutCustomerId:
    """Tests for create_contact without customer_id parameter."""

    @pytest.mark.asyncio
    async def test_create_contact_without_customer_id_creates_no_customer_link(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
        mock_link_service: AsyncMock,
    ) -> None:
        """Test that creating a contact without customer_id does not create a customer link."""
        contact_id = uuid4()

        mock_contact = MagicMock(spec=Contact)
        mock_contact.id = contact_id
        mock_repository.create.return_value = mock_contact

        contact_input = ContactInput(
            first_name="Bob",
            last_name="Wilson",
        )

        result = await contacts_service.create_contact(contact_input)

        assert result == mock_contact
        mock_repository.create.assert_called_once()
        mock_link_service.create_link.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_contact_with_none_customer_id_creates_no_link(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
        mock_link_service: AsyncMock,
    ) -> None:
        """Test that creating a contact with customer_id=None does not create a link."""
        contact_id = uuid4()

        mock_contact = MagicMock(spec=Contact)
        mock_contact.id = contact_id
        mock_repository.create.return_value = mock_contact

        contact_input = ContactInput(
            first_name="Alice",
            last_name="Brown",
            customer_id=None,
        )

        _ = await contacts_service.create_contact(contact_input)

        mock_link_service.create_link.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_contact_with_only_company_id_creates_company_link_only(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
        mock_link_service: AsyncMock,
    ) -> None:
        """Test that creating a contact with only company_id creates only company link."""
        contact_id = uuid4()
        company_id = uuid4()

        mock_contact = MagicMock(spec=Contact)
        mock_contact.id = contact_id
        mock_repository.create.return_value = mock_contact

        contact_input = ContactInput(
            first_name="Charlie",
            last_name="Davis",
            company_id=company_id,
        )

        _ = await contacts_service.create_contact(contact_input)

        mock_link_service.create_link.assert_called_once_with(
            source_type=EntityType.CONTACT,
            source_id=contact_id,
            target_type=EntityType.COMPANY,
            target_id=company_id,
        )


class TestGetContactRelatedEntities:
    """Tests for get_contact_related_entities method."""

    @pytest.mark.asyncio
    async def test_get_contact_related_entities_returns_customers(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
        mock_companies_service: AsyncMock,
        mock_customer_service: AsyncMock,
    ) -> None:
        """Test that get_contact_related_entities returns customers."""
        contact_id = uuid4()
        mock_repository.exists.return_value = True
        mock_companies_service.find_companies_by_contact_id.return_value = []

        # Create mock customers
        mock_customer = MagicMock()
        mock_customer.id = uuid4()
        mock_customer.company_name = "Test Customer"
        mock_customer_service.find_by_entity.return_value = [mock_customer]

        result = await contacts_service.get_contact_related_entities(contact_id)

        mock_customer_service.find_by_entity.assert_called_once_with(
            EntityType.CONTACT, contact_id
        )
        assert len(result.customers) == 1

    @pytest.mark.asyncio
    async def test_get_contact_related_entities_returns_empty_when_no_customers(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
        mock_companies_service: AsyncMock,
        mock_customer_service: AsyncMock,
    ) -> None:
        """Test that get_contact_related_entities returns empty list when no customers."""
        contact_id = uuid4()
        mock_repository.exists.return_value = True
        mock_companies_service.find_companies_by_contact_id.return_value = []
        mock_customer_service.find_by_entity.return_value = []

        result = await contacts_service.get_contact_related_entities(contact_id)

        assert result.customers == []
        assert result.companies == []

    @pytest.mark.asyncio
    async def test_get_contact_related_entities_raises_not_found_for_invalid_contact(
        self,
        contacts_service: ContactsService,
        mock_repository: AsyncMock,
    ) -> None:
        """Test that get_contact_related_entities raises NotFoundError for invalid contact."""
        from app.errors.common_errors import NotFoundError

        contact_id = uuid4()
        mock_repository.exists.return_value = False

        with pytest.raises(NotFoundError):
            _ = await contacts_service.get_contact_related_entities(contact_id)
