from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_related_entities_response import (
    ContactRelatedEntitiesResponse,
)
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.inject import inject


@strawberry.type
class ContactsQueries:
    """GraphQL queries for Contacts entity."""

    @strawberry.field
    @inject
    async def contact(
        self,
        id: UUID,
        service: Injected[ContactsService],
    ) -> ContactResponse:
        """Get a contact by ID."""
        return ContactResponse.from_orm_model(await service.get_contact(id))

    @strawberry.field
    @inject
    async def contacts_by_company(
        self,
        company_id: UUID,
        service: Injected[ContactsService],
    ) -> list[ContactResponse]:
        """Get all contacts for a specific company."""
        contacts = await service.get_contacts_by_company(company_id)
        return ContactResponse.from_orm_model_list(contacts)

    @strawberry.field
    @inject
    async def contact_search(
        self,
        service: Injected[ContactsService],
        search_term: str,
        limit: int = 20,
    ) -> list[ContactResponse]:
        """
        Search contacts by name.

        Args:
            search_term: The search term to match against contact names
            limit: Maximum number of contacts to return (default: 20)

        Returns:
            List of ContactResponse objects matching the search criteria
        """
        return ContactResponse.from_orm_model_list(
            await service.search_contacts(search_term, limit)
        )

    @strawberry.field
    @inject
    async def contact_related_entities(
        self,
        contact_id: UUID,
        service: Injected[ContactsService],
    ) -> ContactRelatedEntitiesResponse:
        """
        Get all entities related to a contact.

        Args:
            contact_id: The contact ID to get related entities for

        Returns:
            ContactRelatedEntitiesResponse containing companies related to the contact
        """
        return await service.get_contact_related_entities(contact_id)
