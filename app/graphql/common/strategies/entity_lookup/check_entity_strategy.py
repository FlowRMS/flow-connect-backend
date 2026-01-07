from typing import override
from uuid import UUID

from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.common.entity_source_type import EntitySourceType
from app.graphql.common.interfaces.entity_lookup_strategy import EntityLookupStrategy
from app.graphql.common.strawberry.entity_response import EntityResponse


class CheckEntityStrategy(EntityLookupStrategy):
    def __init__(self, service: CheckService) -> None:
        super().__init__()
        self.service = service

    @override
    def get_supported_source_type(self) -> EntitySourceType:
        return EntitySourceType.CHECKS

    @override
    async def get_entity(self, entity_id: UUID) -> EntityResponse:
        check = await self.service.find_check_by_id(entity_id)
        return CheckResponse.from_orm_model(check)
