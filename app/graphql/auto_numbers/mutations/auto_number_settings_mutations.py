import strawberry
from aioinject import Injected

from app.graphql.auto_numbers.services.auto_number_settings_service import (
    AutoNumberSettingsService,
)
from app.graphql.auto_numbers.strawberry.auto_number_settings_input import (
    AutoNumberSettingsInput,
)
from app.graphql.auto_numbers.strawberry.auto_number_settings_response import (
    AutoNumberSettingsResponse,
)
from app.graphql.inject import inject


@strawberry.type
class AutoNumberSettingsMutations:
    @strawberry.mutation
    @inject
    async def update_auto_number_settings(
        self,
        inputs: list[AutoNumberSettingsInput],
        service: Injected[AutoNumberSettingsService],
    ) -> list[AutoNumberSettingsResponse]:
        settings = await service.update_settings(inputs)
        return AutoNumberSettingsResponse.from_orm_model_list(settings)
