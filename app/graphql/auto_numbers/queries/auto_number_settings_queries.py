import strawberry
from aioinject import Injected

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
