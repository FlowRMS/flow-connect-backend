"""GraphQL queries for Notes entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.inject import inject
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.jobs.strawberry.job_response import JobType
from app.graphql.links.models.entity_type import EntityType
from app.graphql.notes.services.notes_service import NotesService
from app.graphql.notes.strawberry.note_related_entities_response import (
    NoteRelatedEntitiesResponse,
)
from app.graphql.notes.strawberry.note_response import (
    NoteConversationType,
    NoteType,
)
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_response import TaskType


@strawberry.type
class NotesQueries:
    """GraphQL queries for Notes entity."""

    @strawberry.field
    @inject
    async def note(
        self,
        id: UUID,
        service: Injected[NotesService],
    ) -> NoteType:
        """Get a note by ID."""
        return NoteType.from_orm_model(await service.get_note(id))

    @strawberry.field
    @inject
    async def notes(
        self,
        service: Injected[NotesService],
        limit: int = 20,
        offset: int = 0,
    ) -> list[NoteType]:
        """List notes with pagination."""
        notes = await service.list_notes(limit=limit, offset=offset)
        return [NoteType.from_orm_model(note) for note in notes]

    @strawberry.field
    @inject
    async def notes_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        service: Injected[NotesService],
    ) -> list[NoteType]:
        """Find all notes linked to a specific entity."""
        notes = await service.find_notes_by_entity(entity_type, entity_id)
        return [NoteType.from_orm_model(note) for note in notes]

    @strawberry.field
    @inject
    async def note_conversations(
        self,
        note_id: UUID,
        service: Injected[NotesService],
    ) -> list[NoteConversationType]:
        """Get all conversation entries for a specific note."""
        conversations = await service.get_conversations_by_note(note_id)
        return [
            NoteConversationType.from_orm_model(conversation)
            for conversation in conversations
        ]

    @strawberry.field
    @inject
    async def note_search(
        self,
        service: Injected[NotesService],
        search_term: str,
        limit: int = 20,
    ) -> list[NoteType]:
        """
        Search notes by title or content.

        Args:
            search_term: The search term to match against note title or content
            limit: Maximum number of notes to return (default: 20)

        Returns:
            List of NoteType objects matching the search criteria
        """
        return NoteType.from_orm_model_list(
            await service.search_notes(search_term, limit)
        )

    @strawberry.field
    @inject
    async def note_related_entities(
        self,
        note_id: UUID,
        notes_service: Injected[NotesService],
        jobs_service: Injected[JobsService],
        tasks_service: Injected[TasksService],
        contacts_service: Injected[ContactsService],
        companies_service: Injected[CompaniesService],
        pre_opportunities_service: Injected[PreOpportunitiesService],
    ) -> NoteRelatedEntitiesResponse:
        """Get all entities related to a note."""
        # Verify note exists
        _ = await notes_service.get_note(note_id)

        # Fetch related entities
        jobs = await jobs_service.get_jobs_by_note(note_id)
        tasks = await tasks_service.find_tasks_by_note_id(note_id)
        contacts = await contacts_service.find_contacts_by_note_id(note_id)
        companies = await companies_service.find_companies_by_note_id(note_id)
        pre_opportunities = await pre_opportunities_service.find_by_entity(
            EntityType.NOTE, note_id
        )

        return NoteRelatedEntitiesResponse(
            jobs=JobType.from_orm_model_list(jobs),
            tasks=TaskType.from_orm_model_list(tasks),
            contacts=ContactResponse.from_orm_model_list(contacts),
            companies=CompanyResponse.from_orm_model_list(companies),
            pre_opportunities=PreOpportunityLiteResponse.from_orm_model_list(
                pre_opportunities
            ),
        )
