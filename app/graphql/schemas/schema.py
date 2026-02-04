import datetime
import decimal

import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from fastapi import UploadFile
from strawberry.file_uploads import Upload
from strawberry.tools import merge_types

import app.graphql
from app.core.container import create_container
from app.core.middleware.commission_masking_extension import CommissionMaskingExtension
from app.core.middleware.graphql_middleware import GraphQLMiddleware
from app.graphql.class_discovery import class_discovery
from app.graphql.inject import context_setter
from app.graphql.schemas.date_time_scalar import DateTimeScalar
from app.graphql.schemas.decimal_scalar import DecimalScalar
from app.graphql.schemas.json_scalar import JsonScalar

Query = merge_types(
    name="Query",
    types=tuple(
        class_discovery(
            module=app.graphql,
            mode_suffix="queries",
            class_suffix="Queries",
        )
    ),
)

Mutation = merge_types(
    name="Mutation",
    types=tuple(
        class_discovery(
            module=app.graphql,
            mode_suffix="mutations",
            class_suffix="Mutations",
        )
    ),
)


schema = strawberry.federation.Schema(
    Query,
    mutation=Mutation,
    extensions=[
        AioInjectExtension(
            container=create_container(),
            context_setter=context_setter,
        ),
        GraphQLMiddleware,
        CommissionMaskingExtension,
    ],
    scalar_overrides={
        datetime.datetime: DateTimeScalar,
        UploadFile: Upload,
        decimal.Decimal: DecimalScalar,
        strawberry.scalars.JSON: JsonScalar,
    },
    federation_version="2.0",
)
