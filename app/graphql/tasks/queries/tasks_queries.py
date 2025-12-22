from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.inject import inject
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.jobs.strawberry.job_response import JobType
from app.graphql.notes.services.notes_service import NotesService
from app.graphql.notes.strawberry.note_response import NoteType
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_response import OrderResponse
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_response import QuoteResponse
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_conversation_response import (
    TaskConversationType,
)
from app.graphql.tasks.strawberry.task_related_entities_response import (
    TaskRelatedEntitiesResponse,
)
from app.graphql.tasks.strawberry.task_response import TaskType
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_response import CustomerResponse
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_response import FactoryResponse
from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.v2.core.products.strawberry.product_response import ProductResponse


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
        quote_service: Injected[QuoteService],
        order_service: Injected[OrderService],
        invoice_service: Injected[InvoiceService],
        check_service: Injected[CheckService],
        factory_service: Injected[FactoryService],
        product_service: Injected[ProductService],
        customer_service: Injected[CustomerService],
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
        quotes = await quote_service.find_by_entity(EntityType.TASK, task_id)
        orders = await order_service.find_by_entity(EntityType.TASK, task_id)
        invoices = await invoice_service.find_by_entity(EntityType.TASK, task_id)
        checks = await check_service.find_by_entity(EntityType.TASK, task_id)
        factories = await factory_service.find_by_entity(EntityType.TASK, task_id)
        products = await product_service.find_by_entity(EntityType.TASK, task_id)
        customers = await customer_service.find_by_entity(EntityType.TASK, task_id)

        return TaskRelatedEntitiesResponse(
            jobs=JobType.from_orm_model_list(jobs),
            contacts=ContactResponse.from_orm_model_list(contacts),
            companies=CompanyResponse.from_orm_model_list(companies),
            notes=NoteType.from_orm_model_list(notes),
            pre_opportunities=PreOpportunityLiteResponse.from_orm_model_list(
                pre_opportunities
            ),
            quotes=QuoteResponse.from_orm_model_list(quotes),
            orders=OrderResponse.from_orm_model_list(orders),
            invoices=InvoiceResponse.from_orm_model_list(invoices),
            checks=CheckResponse.from_orm_model_list(checks),
            factories=FactoryResponse.from_orm_model_list(factories),
            products=ProductResponse.from_orm_model_list(products),
            customers=CustomerResponse.from_orm_model_list(customers),
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
