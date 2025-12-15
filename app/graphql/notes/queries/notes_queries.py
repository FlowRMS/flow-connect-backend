"""GraphQL queries for Notes entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

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
from app.graphql.links.models.entity_type import EntityType
from app.graphql.notes.services.notes_service import NotesService
from app.graphql.notes.strawberry.note_related_entities_response import (
    NoteRelatedEntitiesResponse,
)
from app.graphql.notes.strawberry.note_response import (
    NoteConversationType,
    NoteType,
)
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
from app.graphql.tasks.strawberry.task_response import TaskType
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_response import CustomerResponse
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_response import FactoryResponse
from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.v2.core.products.strawberry.product_response import ProductResponse


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
        quote_service: Injected[QuoteService],
        order_service: Injected[OrderService],
        invoice_service: Injected[InvoiceService],
        check_service: Injected[CheckService],
        factory_service: Injected[FactoryService],
        product_service: Injected[ProductService],
        customer_service: Injected[CustomerService],
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
        quotes = await quote_service.find_by_entity(EntityType.NOTE, note_id)
        orders = await order_service.find_by_entity(EntityType.NOTE, note_id)
        invoices = await invoice_service.find_by_entity(EntityType.NOTE, note_id)
        checks = await check_service.find_by_entity(EntityType.NOTE, note_id)
        factories = await factory_service.find_by_entity(EntityType.NOTE, note_id)
        products = await product_service.find_by_entity(EntityType.NOTE, note_id)
        customers = await customer_service.find_by_entity(EntityType.NOTE, note_id)

        return NoteRelatedEntitiesResponse(
            jobs=JobType.from_orm_model_list(jobs),
            tasks=TaskType.from_orm_model_list(tasks),
            contacts=ContactResponse.from_orm_model_list(contacts),
            companies=CompanyResponse.from_orm_model_list(companies),
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
