from typing import override
from uuid import UUID

from app.errors.common_errors import NotFoundError
from app.graphql.common.interfaces.related_entities_strategy import (
    RelatedEntitiesStrategy,
)
from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.common.strawberry.related_entities_response import (
    RelatedEntitiesResponse,
)
from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyLiteResponse
from app.graphql.contacts.repositories.contacts_repository import ContactsRepository


class ContactRelatedEntitiesStrategy(RelatedEntitiesStrategy):
    def __init__(
        self,
        repository: ContactsRepository,
        companies_service: CompaniesService,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.companies_service = companies_service

    @override
    def get_supported_source_type(self) -> LandingSourceType:
        return LandingSourceType.CONTACTS

    @override
    async def get_related_entities(self, entity_id: UUID) -> RelatedEntitiesResponse:
        if not await self.repository.exists(entity_id):
            raise NotFoundError(str(entity_id))

        companies = await self.companies_service.find_companies_by_contact_id(entity_id)

        return RelatedEntitiesResponse(
            source_type=LandingSourceType.CONTACTS,
            source_entity_id=entity_id,
            companies=CompanyLiteResponse.from_orm_model_list(companies),
        )
