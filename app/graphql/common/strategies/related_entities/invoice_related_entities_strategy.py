from typing import override
from uuid import UUID

from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NotFoundError
from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_response import CheckLiteResponse
from app.graphql.common.interfaces.related_entities_strategy import (
    RelatedEntitiesStrategy,
)
from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.common.strawberry.related_entities_response import (
    RelatedEntitiesResponse,
)
from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyLiteResponse
from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.invoices.repositories.invoices_repository import InvoicesRepository
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.jobs.strawberry.job_response import JobLiteType
from app.graphql.notes.services.notes_service import NotesService
from app.graphql.notes.strawberry.note_response import NoteType
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_response import TaskType
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


class InvoiceRelatedEntitiesStrategy(RelatedEntitiesStrategy):
    def __init__(
        self,
        repository: InvoicesRepository,
        notes_service: NotesService,
        tasks_service: TasksService,
        companies_service: CompaniesService,
        contacts_service: ContactsService,
        jobs_service: JobsService,
        quote_service: QuoteService,
        order_service: OrderService,
        check_service: CheckService,
        factory_service: FactoryService,
        product_service: ProductService,
        customer_service: CustomerService,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.notes_service = notes_service
        self.tasks_service = tasks_service
        self.companies_service = companies_service
        self.contacts_service = contacts_service
        self.jobs_service = jobs_service
        self.quote_service = quote_service
        self.order_service = order_service
        self.check_service = check_service
        self.factory_service = factory_service
        self.product_service = product_service
        self.customer_service = customer_service

    @override
    def get_supported_source_type(self) -> LandingSourceType:
        return LandingSourceType.INVOICES

    @override
    async def get_related_entities(self, entity_id: UUID) -> RelatedEntitiesResponse:
        if not await self.repository.exists(entity_id):
            raise NotFoundError(str(entity_id))

        notes = await self.notes_service.find_notes_by_entity(
            EntityType.INVOICE, entity_id
        )
        tasks = await self.tasks_service.find_tasks_by_entity(
            EntityType.INVOICE, entity_id
        )
        contacts = await self.contacts_service.find_by_entity(
            EntityType.INVOICE, entity_id
        )
        companies = await self.companies_service.find_by_entity(
            EntityType.INVOICE, entity_id
        )
        jobs = await self.jobs_service.find_by_entity(EntityType.INVOICE, entity_id)
        quotes = await self.quote_service.find_by_entity(EntityType.INVOICE, entity_id)
        orders = await self.order_service.find_by_entity(EntityType.INVOICE, entity_id)
        checks = await self.check_service.find_by_entity(EntityType.INVOICE, entity_id)
        factories = await self.factory_service.find_by_entity(
            EntityType.INVOICE, entity_id
        )
        products = await self.product_service.find_by_entity(
            EntityType.INVOICE, entity_id
        )
        customers = await self.customer_service.find_by_entity(
            EntityType.INVOICE, entity_id
        )

        return RelatedEntitiesResponse(
            source_type=LandingSourceType.INVOICES,
            source_entity_id=entity_id,
            notes=NoteType.from_orm_model_list(notes),
            tasks=TaskType.from_orm_model_list(tasks),
            contacts=ContactResponse.from_orm_model_list(contacts),
            companies=CompanyLiteResponse.from_orm_model_list(companies),
            jobs=JobLiteType.from_orm_model_list(jobs),
            quotes=QuoteLiteResponse.from_orm_model_list(quotes),
            orders=OrderLiteResponse.from_orm_model_list(orders),
            checks=CheckLiteResponse.from_orm_model_list(checks),
            factories=FactoryLiteResponse.from_orm_model_list(factories),
            products=ProductLiteResponse.from_orm_model_list(products),
            customers=CustomerLiteResponse.from_orm_model_list(customers),
        )
