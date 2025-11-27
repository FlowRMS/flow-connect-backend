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

# from app.graphql.class_discovery import types_discovery
from app.graphql.companies.mutations.companies_mutations import CompaniesMutations
from app.graphql.companies.queries.companies_queries import CompaniesQueries
from app.graphql.contacts.mutations.contacts_mutations import ContactsMutations
from app.graphql.contacts.queries.contacts_queries import ContactsQueries
from app.graphql.inject import context_setter
from app.graphql.jobs.mutations.jobs_mutations import JobsMutations
from app.graphql.jobs.queries.jobs_landing_queries import JobsLandingQueries

# Import entity queries and mutations
from app.graphql.jobs.queries.jobs_queries import JobsQueries
from app.graphql.jobs.strawberry.job_landing_page_response import JobLandingPageResponse
from app.graphql.links.mutations.links_mutations import LinksMutations
from app.graphql.links.queries.links_queries import LinksQueries
from app.graphql.schemas.date_time_scalar import DateTimeScalar
from app.graphql.schemas.decimal_scalar import DecimalScalar
from app.graphql.schemas.id_scalar import IdScalar
from app.graphql.schemas.json_scalar import JsonScalar
from app.graphql.tasks.mutations.tasks_mutations import TasksMutations
from app.graphql.tasks.queries.tasks_queries import TasksQueries

Query = merge_types(
    name="Query",
    types=(
        JobsQueries,
        TasksQueries,
        CompaniesQueries,
        ContactsQueries,
        LinksQueries,
        JobsLandingQueries,
    ),
)

Mutation = merge_types(
    name="Mutation",
    types=(
        JobsMutations,
        TasksMutations,
        CompaniesMutations,
        ContactsMutations,
        LinksMutations,
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
    types=(JobLandingPageResponse,),
)
