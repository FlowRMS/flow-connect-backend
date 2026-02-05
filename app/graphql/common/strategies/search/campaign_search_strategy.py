from typing import Any, override

from commons.db.v6.crm.campaigns.campaign_model import Campaign
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class CampaignSearchQueryBuilder(SearchQueryBuilder[Campaign]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            Campaign.name,
            Campaign.description,
            Campaign.email_subject,
            Campaign.email_body,
        ]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Campaign.name

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(Campaign.description, Campaign.email_subject)


class CampaignSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = CampaignSearchQueryBuilder(Campaign, SourceType.CAMPAIGN)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.CAMPAIGN

    @override
    def get_model_class(self) -> type[Any]:
        return Campaign

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
