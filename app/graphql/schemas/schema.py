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
from app.graphql.schemas.date_time_scalar import DateTimeScalar
from app.graphql.schemas.decimal_scalar import DecimalScalar
from app.graphql.schemas.id_scalar import IdScalar
from app.graphql.schemas.json_scalar import JsonScalar


@strawberry.type
class Dummy:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, world!"


Query = merge_types(
    name="Query",
    types=(Dummy,),
)

# Mutation = merge_types(
#     name="Mutation",
#     types=(ReportTemplateMutations,),
# )


schema = strawberry.Schema(  # pyright: ignore[reportArgumentType]
    Query,
    # mutation=Mutation,
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
