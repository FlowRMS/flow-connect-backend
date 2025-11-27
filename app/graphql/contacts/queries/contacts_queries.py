from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.contacts.services.contacts_service import ContactsService
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
