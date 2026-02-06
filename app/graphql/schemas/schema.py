import datetime
import decimal
from typing import Any

import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from fastapi import UploadFile
from strawberry.extensions.mask_errors import MaskErrors
from strawberry.file_uploads import Upload

from app.core.container import create_container
from app.core.middleware.graphql_middleware import GraphQLMiddleware
from app.graphql.connections.mutations import ConnectionMutations
from app.graphql.di import context_setter
from app.graphql.error_handler import should_mask_error
from app.graphql.geography.mutations.connection_territory_mutations import (
    ConnectionTerritoryMutations,
)
from app.graphql.organizations.mutations import OrganizationMutations
from app.graphql.organizations.queries import (
    ConnectionQueries,
    UserOrganizationQueries,
)
from app.graphql.pos.agreement.mutations.agreement_mutations import AgreementMutations
from app.graphql.pos.dashboard.queries import DashboardQueries
from app.graphql.pos.data_exchange.mutations import (
    ExchangeFileMutations,
    ReceivedExchangeFileMutations,
)
from app.graphql.pos.data_exchange.queries import (
    ExchangeFileQueries,
    ReceivedExchangeFileQueries,
)
from app.graphql.pos.field_map.mutations.field_map_mutations import FieldMapMutations
from app.graphql.pos.field_map.queries.field_map_queries import FieldMapQueries
from app.graphql.pos.organization_alias.mutations import OrganizationAliasMutations
from app.graphql.pos.organization_alias.queries import OrganizationAliasQueries
from app.graphql.pos.validations.mutations import PrefixPatternMutations
from app.graphql.pos.validations.queries import (
    FileValidationIssueQueries,
    PrefixPatternQueries,
    ValidationRuleQueries,
)
from app.graphql.schemas.date_time_scalar import DateTimeScalar
from app.graphql.schemas.decimal_scalar import DecimalScalar
from app.graphql.schemas.json_scalar import JsonScalar
from app.graphql.settings.organization_preferences.mutations.organization_preference_mutations import (
    OrganizationPreferenceMutations,
)
from app.graphql.settings.organization_preferences.queries.organization_preference_queries import (
    OrganizationPreferenceQueries,
)


@strawberry.type
class Query(
    ConnectionQueries,
    UserOrganizationQueries,
    OrganizationPreferenceQueries,
    DashboardQueries,
    FieldMapQueries,
    OrganizationAliasQueries,
    FileValidationIssueQueries,
    PrefixPatternQueries,
    ValidationRuleQueries,
    ExchangeFileQueries,
    ReceivedExchangeFileQueries,
):
    @strawberry.field()
    def health(self) -> str:
        return "ok"


@strawberry.type
class Mutation(
    ConnectionMutations,
    ConnectionTerritoryMutations,
    AgreementMutations,
    OrganizationMutations,
    OrganizationPreferenceMutations,
    FieldMapMutations,
    OrganizationAliasMutations,
    PrefixPatternMutations,
    ExchangeFileMutations,
    ReceivedExchangeFileMutations,
):
    @strawberry.mutation()
    def ping(self) -> str:
        return "pong"


scalar_overrides: dict[object, Any] = {
    datetime.datetime: DateTimeScalar,
    UploadFile: Upload,
    decimal.Decimal: DecimalScalar,
    strawberry.scalars.JSON: JsonScalar,
}

schema = strawberry.Schema(
    Query,
    mutation=Mutation,
    extensions=[
        AioInjectExtension(
            container=create_container(),
            context_setter=context_setter,
        ),
        GraphQLMiddleware,
        MaskErrors(should_mask_error=should_mask_error),
    ],
    scalar_overrides=scalar_overrides,
)
