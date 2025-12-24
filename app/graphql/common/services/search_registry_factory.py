from app.graphql.common.interfaces.search_query_interface import (
    SearchQueryStrategyRegistry,
)
from app.graphql.common.strategies.search import (
    CampaignSearchStrategy,
    CompanySearchStrategy,
    ContactSearchStrategy,
    CustomerSearchStrategy,
    FactorySearchStrategy,
    JobSearchStrategy,
    NoteSearchStrategy,
    PreOpportunitySearchStrategy,
    ProductSearchStrategy,
    QuoteSearchStrategy,
    SpecSheetSearchStrategy,
    TaskSearchStrategy,
)


def create_search_strategy_registry() -> SearchQueryStrategyRegistry:
    registry = SearchQueryStrategyRegistry()

    strategies = [
        ContactSearchStrategy(),
        CompanySearchStrategy(),
        JobSearchStrategy(),
        TaskSearchStrategy(),
        NoteSearchStrategy(),
        CampaignSearchStrategy(),
        QuoteSearchStrategy(),
        PreOpportunitySearchStrategy(),
        SpecSheetSearchStrategy(),
        CustomerSearchStrategy(),
        FactorySearchStrategy(),
        ProductSearchStrategy(),
    ]

    for strategy in strategies:
        registry.register(strategy)

    return registry
