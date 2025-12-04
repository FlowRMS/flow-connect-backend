import datetime
import decimal

import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from fastapi import UploadFile
from strawberry.file_uploads import Upload
from strawberry.tools import merge_types

# import app.graphql
from app.core.container import create_container
from app.core.middleware.graphql_middleware import GraphQLMiddleware
from app.graphql.checks.queries.checks_queries import ChecksQueries

# from app.graphql.class_discovery import types_discovery
from app.graphql.common.queries.landing_page_queries import LandingPageQueries
from app.graphql.companies.mutations.companies_mutations import CompaniesMutations
from app.graphql.companies.queries.companies_queries import CompaniesQueries
from app.graphql.contacts.mutations.contacts_mutations import ContactsMutations
from app.graphql.contacts.queries.contacts_queries import ContactsQueries
from app.graphql.customers.queries.customers_queries import CustomersQueries
from app.graphql.factories.queries.factories_queries import FactoriesQueries
from app.graphql.inject import context_setter
from app.graphql.invoices.queries.invoices_queries import InvoicesQueries
from app.graphql.jobs.mutations.jobs_mutations import JobsMutations
from app.graphql.jobs.queries.jobs_queries import JobsQueries
from app.graphql.links.mutations.links_mutations import LinksMutations
from app.graphql.links.queries.links_queries import LinksQueries
from app.graphql.notes.mutations.notes_mutations import NotesMutations
from app.graphql.notes.queries.notes_queries import NotesQueries
from app.graphql.orders.queries.orders_queries import OrdersQueries
from app.graphql.pre_opportunities.mutations.pre_opportunities_mutations import (
    PreOpportunitiesMutations,
)
from app.graphql.pre_opportunities.queries.pre_opportunities_queries import (
    PreOpportunitiesQueries,
)
from app.graphql.products.queries.products_queries import ProductsQueries
from app.graphql.quotes.queries.quotes_queries import QuotesQueries
from app.graphql.schemas.date_time_scalar import DateTimeScalar
from app.graphql.schemas.decimal_scalar import DecimalScalar
from app.graphql.schemas.id_scalar import IdScalar
from app.graphql.schemas.json_scalar import JsonScalar
from app.graphql.tasks.mutations.tasks_mutations import TasksMutations
from app.graphql.tasks.queries.tasks_queries import TasksQueries
from app.graphql.users.queries.users_queries import UsersQueries

Query = merge_types(
    name="Query",
    types=(
        JobsQueries,
        TasksQueries,
        NotesQueries,
        CompaniesQueries,
        ContactsQueries,
        PreOpportunitiesQueries,
        ProductsQueries,
        FactoriesQueries,
        CustomersQueries,
        QuotesQueries,
        OrdersQueries,
        InvoicesQueries,
        ChecksQueries,
        LandingPageQueries,
        UsersQueries,
        LinksQueries,
    ),
)

Mutation = merge_types(
    name="Mutation",
    types=(
        JobsMutations,
        TasksMutations,
        NotesMutations,
        CompaniesMutations,
        ContactsMutations,
        LinksMutations,
        PreOpportunitiesMutations,
    ),
)


schema = strawberry.Schema(  # pyright: ignore[reportArgumentType]
    Query,
    mutation=Mutation,
    extensions=[
        AioInjectExtension(
            container=create_container(),
            context_setter=context_setter,
        ),
        GraphQLMiddleware,
    ],
    scalar_overrides={
        strawberry.ID: IdScalar,
        datetime.datetime: DateTimeScalar,
        UploadFile: Upload,
        decimal.Decimal: DecimalScalar,
        strawberry.scalars.JSON: JsonScalar,
    },
)
