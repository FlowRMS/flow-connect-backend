import datetime
import decimal

import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from fastapi import UploadFile
from strawberry.file_uploads import Upload

from app.admin.inject import admin_context_setter
from app.admin.middleware import AdminGraphQLMiddleware
from app.admin.tenants.mutations.tenants_mutations import TenantsMutations
from app.admin.tenants.queries.tenants_queries import TenantsQueries
from app.core.container import create_container
from app.graphql.schemas.date_time_scalar import DateTimeScalar
from app.graphql.schemas.decimal_scalar import DecimalScalar
from app.graphql.schemas.id_scalar import IdScalar
from app.graphql.schemas.json_scalar import JsonScalar

schema = strawberry.Schema(
    query=TenantsQueries,
    mutation=TenantsMutations,
    extensions=[
        AioInjectExtension(
            container=create_container(),
            context_setter=admin_context_setter,
        ),
        AdminGraphQLMiddleware,
    ],
    scalar_overrides={
        strawberry.ID: IdScalar,
        datetime.datetime: DateTimeScalar,
        UploadFile: Upload,
        decimal.Decimal: DecimalScalar,
        strawberry.scalars.JSON: JsonScalar,
    },
)
