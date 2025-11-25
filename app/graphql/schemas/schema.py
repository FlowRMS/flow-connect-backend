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
from app.graphql.inject import context_setter
from app.graphql.jobs.mutations.jobs_mutations import JobsMutations

# Import entity queries and mutations
from app.graphql.jobs.queries.jobs_queries import JobsQueries
from app.graphql.schemas.date_time_scalar import DateTimeScalar
from app.graphql.schemas.decimal_scalar import DecimalScalar
from app.graphql.schemas.id_scalar import IdScalar
from app.graphql.schemas.json_scalar import JsonScalar
from app.graphql.tasks.mutations.tasks_mutations import TasksMutations
from app.graphql.tasks.queries.tasks_queries import TasksQueries

Query = merge_types(
    name="Query",
    types=(JobsQueries, TasksQueries),
)

Mutation = merge_types(
    name="Mutation",
    types=(JobsMutations, TasksMutations),
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
