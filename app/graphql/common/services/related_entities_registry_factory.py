from app.graphql.checks.services.check_service import CheckService
from app.graphql.common.interfaces.related_entities_strategy import (
    RelatedEntitiesStrategyRegistry,
)
from app.graphql.common.strategies.related_entities import (
    ContactRelatedEntitiesStrategy,
    FactoryRelatedEntitiesStrategy,
    JobRelatedEntitiesStrategy,
    NoteRelatedEntitiesStrategy,
    PreOpportunityRelatedEntitiesStrategy,
    TaskRelatedEntitiesStrategy,
)
from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.contacts.repositories.contacts_repository import ContactsRepository
from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.notes.repositories.notes_repository import NotesRepository
from app.graphql.notes.services.notes_service import NotesService
from app.graphql.orders.services.order_service import OrderService
from app.graphql.pre_opportunities.repositories.pre_opportunities_repository import (
    PreOpportunitiesRepository,
)
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.tasks.repositories.tasks_repository import TasksRepository
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.factories.repositories.factories_repository import (
    FactoriesRepository,
)
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.products.services.product_service import ProductService


def create_related_entities_registry(
    jobs_repository: JobsRepository,
    contacts_repository: ContactsRepository,
    notes_repository: NotesRepository,
    tasks_repository: TasksRepository,
    pre_opportunities_repository: PreOpportunitiesRepository,
    factories_repository: FactoriesRepository,
    jobs_service: JobsService,
    notes_service: NotesService,
    tasks_service: TasksService,
    contacts_service: ContactsService,
    companies_service: CompaniesService,
    pre_opportunities_service: PreOpportunitiesService,
    quote_service: QuoteService,
    order_service: OrderService,
    invoice_service: InvoiceService,
    check_service: CheckService,
    factory_service: FactoryService,
    product_service: ProductService,
    customer_service: CustomerService,
) -> RelatedEntitiesStrategyRegistry:
    registry = RelatedEntitiesStrategyRegistry()

    strategies = [
        JobRelatedEntitiesStrategy(
            repository=jobs_repository,
            notes_service=notes_service,
            tasks_service=tasks_service,
            companies_service=companies_service,
            contacts_service=contacts_service,
            pre_opportunities_service=pre_opportunities_service,
            quote_service=quote_service,
            order_service=order_service,
            invoice_service=invoice_service,
            check_service=check_service,
            factory_service=factory_service,
            product_service=product_service,
            customer_service=customer_service,
        ),
        ContactRelatedEntitiesStrategy(
            repository=contacts_repository,
            jobs_service=jobs_service,
            notes_service=notes_service,
            tasks_service=tasks_service,
            companies_service=companies_service,
            pre_opportunities_service=pre_opportunities_service,
            quote_service=quote_service,
            order_service=order_service,
            invoice_service=invoice_service,
            check_service=check_service,
            factory_service=factory_service,
            product_service=product_service,
            customer_service=customer_service,
        ),
        NoteRelatedEntitiesStrategy(
            repository=notes_repository,
            jobs_service=jobs_service,
            tasks_service=tasks_service,
            contacts_service=contacts_service,
            companies_service=companies_service,
            pre_opportunities_service=pre_opportunities_service,
            quote_service=quote_service,
            order_service=order_service,
            invoice_service=invoice_service,
            check_service=check_service,
            factory_service=factory_service,
            product_service=product_service,
            customer_service=customer_service,
        ),
        TaskRelatedEntitiesStrategy(
            repository=tasks_repository,
            jobs_service=jobs_service,
            notes_service=notes_service,
            contacts_service=contacts_service,
            companies_service=companies_service,
            pre_opportunities_service=pre_opportunities_service,
            quote_service=quote_service,
            order_service=order_service,
            invoice_service=invoice_service,
            check_service=check_service,
            factory_service=factory_service,
            product_service=product_service,
            customer_service=customer_service,
        ),
        PreOpportunityRelatedEntitiesStrategy(
            repository=pre_opportunities_repository,
            jobs_service=jobs_service,
            notes_service=notes_service,
            tasks_service=tasks_service,
            contacts_service=contacts_service,
            companies_service=companies_service,
            quote_service=quote_service,
            order_service=order_service,
            invoice_service=invoice_service,
            check_service=check_service,
            factory_service=factory_service,
            product_service=product_service,
            customer_service=customer_service,
        ),
        FactoryRelatedEntitiesStrategy(
            repository=factories_repository,
            notes_service=notes_service,
            tasks_service=tasks_service,
            contacts_service=contacts_service,
            order_service=order_service,
            invoice_service=invoice_service,
            check_service=check_service,
            product_service=product_service,
        ),
    ]

    for strategy in strategies:
        registry.register(strategy)

    return registry
