from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_input import ContactInput
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.inject import inject


@strawberry.type
class ContactsMutations:
    """GraphQL mutations for Contacts entity."""

    @strawberry.mutation
    @inject
    async def create_contact(
        self,
        input: ContactInput,
        service: Injected[ContactsService],
    ) -> ContactResponse:
        """Create a new contact."""
        return ContactResponse.from_orm_model(
            await service.create_contact(contact_input=input)
        )

    @strawberry.mutation
    @inject
    async def delete_contact(
        self,
        id: UUID,
        service: Injected[ContactsService],
    ) -> bool:
        """Delete a contact by ID."""
        return await service.delete_contact(contact_id=id)
