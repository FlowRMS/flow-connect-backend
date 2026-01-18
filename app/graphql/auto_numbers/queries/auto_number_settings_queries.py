import strawberry
from aioinject import Injected
from commons.db.v6 import AutoNumberEntityType

from app.graphql.auto_numbers.services.auto_number_settings_service import (
    AutoNumberSettingsService,
)
from app.graphql.auto_numbers.strawberry.auto_number_settings_response import (
    AutoNumberSettingsResponse,
)
from app.graphql.inject import inject


@strawberry.type
class AutoNumberSettingsQueries:
    @strawberry.field
    @inject
    async def auto_number_settings(
        self,
        service: Injected[AutoNumberSettingsService],
    ) -> list[AutoNumberSettingsResponse]:
        settings = await service.get_settings()
        return AutoNumberSettingsResponse.from_orm_model_list(settings)

    @strawberry.field
    @inject
    async def auto_number_setting(
        self,
        service: Injected[AutoNumberSettingsService],
        entity_type: AutoNumberEntityType,
    ) -> AutoNumberSettingsResponse | None:
        return AutoNumberSettingsResponse.from_orm_model_optional(
            await service.get_setting(entity_type)
        )
