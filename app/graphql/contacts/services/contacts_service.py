from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.contacts.models.contact_model import Contact
from app.graphql.contacts.repositories.contacts_repository import ContactsRepository
from app.graphql.contacts.strawberry.contact_input import ContactInput


class ContactsService:
    """Service for Contacts entity business logic."""

    def __init__(
        self,
        repository: ContactsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def create_contact(self, contact_input: ContactInput) -> Contact:
        """Create a new contact."""
        contact = contact_input.to_orm_model()
        return await self.repository.create(contact)

    async def delete_contact(self, contact_id: UUID | str) -> bool:
        """Delete a contact by ID."""
        if not await self.repository.exists(contact_id):
            raise NotFoundError(str(contact_id))
        return await self.repository.delete(contact_id)

    async def get_contact(self, contact_id: UUID | str) -> Contact:
        """Get a contact by ID."""
        contact = await self.repository.get_by_id(contact_id)
        if not contact:
            raise NotFoundError(str(contact_id))
        return contact

    async def get_contacts_by_company(self, company_id: UUID) -> list[Contact]:
        """Get all contacts for a specific company."""
        return await self.repository.get_by_company_id(company_id)

    async def find_contacts_by_job_id(self, job_id: UUID) -> list[Contact]:
        """
        Find all contacts linked to the given job ID.

        Args:
            job_id: The job ID to find contacts for

        Returns:
            List of Contact objects linked to the given job ID
        """
        return await self.repository.find_by_job_id(job_id)

    async def update_contact(
        self, contact_id: UUID, contact_input: ContactInput
    ) -> Contact:
        """
        Update an existing contact.

        Args:
            contact_id: The contact ID to update
            contact_input: The updated contact data

        Returns:
            The updated contact entity

        Raises:
            NotFoundError: If the contact doesn't exist
        """
        if not await self.repository.exists(contact_id):
            raise NotFoundError(str(contact_id))

        contact = contact_input.to_orm_model()
        contact.id = contact_id
        return await self.repository.update(contact)

    async def search_contacts(self, search_term: str, limit: int = 20) -> list[Contact]:
        """
        Search contacts by name.

        Args:
            search_term: The search term to match against contact names
            limit: Maximum number of contacts to return (default: 20)

        Returns:
            List of Contact objects matching the search criteria
        """
        return await self.repository.search_by_name(search_term, limit)

    async def find_contacts_by_task_id(self, task_id: UUID) -> list[Contact]:
        """Find all contacts linked to the given task ID."""
        return await self.repository.find_by_task_id(task_id)

    async def find_contacts_by_note_id(self, note_id: UUID) -> list[Contact]:
        """Find all contacts linked to the given note ID."""
        return await self.repository.find_by_note_id(note_id)
