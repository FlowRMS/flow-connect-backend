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
from app.graphql.notes.strawberry.note_response import NoteType
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_conversation_response import (
    TaskConversationType,
)
from app.graphql.tasks.strawberry.task_related_entities_response import (
    TaskRelatedEntitiesResponse,
)
from app.graphql.tasks.strawberry.task_response import TaskType


@strawberry.type
class TasksQueries:
    """GraphQL queries for Tasks entity."""

    @strawberry.field
    @inject
    async def task(
        self,
        id: UUID,
        service: Injected[TasksService],
    ) -> TaskType:
        """Get a task by ID."""
        return TaskType.from_orm_model(await service.get_task(id))

    @strawberry.field
    @inject
    async def task_conversations(
        self,
        task_id: UUID,
        service: Injected[TasksService],
    ) -> list[TaskConversationType]:
        """Get all conversation entries for a specific task."""
        conversations = await service.get_conversations_by_task(task_id)
        return [
            TaskConversationType.from_orm_model(conversation)
            for conversation in conversations
        ]

    @strawberry.field
    @inject
    async def task_search(
        self,
        service: Injected[TasksService],
        search_term: str,
        limit: int = 20,
    ) -> list[TaskType]:
        """
        Search tasks by title.

        Args:
            search_term: The search term to match against task title
            limit: Maximum number of tasks to return (default: 20)

        Returns:
            List of TaskType objects matching the search criteria
        """
        return TaskType.from_orm_model_list(
            await service.search_tasks(search_term, limit)
        )

    @strawberry.field
    @inject
    async def task_related_entities(
        self,
        task_id: UUID,
        tasks_service: Injected[TasksService],
        jobs_service: Injected[JobsService],
        contacts_service: Injected[ContactsService],
        companies_service: Injected[CompaniesService],
        notes_service: Injected[NotesService],
        pre_opportunities_service: Injected[PreOpportunitiesService],
    ) -> TaskRelatedEntitiesResponse:
        """Get all entities related to a task."""
        # Verify task exists
        _ = await tasks_service.get_task(task_id)

        # Fetch related entities
        jobs = await jobs_service.get_jobs_by_task(task_id)
        contacts = await contacts_service.find_contacts_by_task_id(task_id)
        companies = await companies_service.find_companies_by_task_id(task_id)
        notes = await notes_service.find_notes_by_entity(EntityType.TASK, task_id)
        pre_opportunities = await pre_opportunities_service.find_by_entity(
            EntityType.TASK, task_id
        )

        return TaskRelatedEntitiesResponse(
            jobs=JobType.from_orm_model_list(jobs),
            contacts=ContactResponse.from_orm_model_list(contacts),
            companies=CompanyResponse.from_orm_model_list(companies),
            notes=NoteType.from_orm_model_list(notes),
            pre_opportunities=PreOpportunityLiteResponse.from_orm_model_list(
                pre_opportunities
            ),
        )

    @strawberry.field
    @inject
    async def tasks_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        service: Injected[TasksService],
    ) -> list[TaskType]:
        """
        Find all tasks linked to a specific entity.

        Args:
            entity_type: The type of entity to find tasks for
            entity_id: The ID of the entity

        Returns:
            List of TaskType objects linked to the entity
        """
        tasks = await service.find_tasks_by_entity(entity_type, entity_id)
        return TaskType.from_orm_model_list(tasks)
