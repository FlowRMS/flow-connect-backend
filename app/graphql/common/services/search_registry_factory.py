from app.graphql.common.interfaces.search_query_interface import (
    SearchQueryStrategyRegistry,
)
from app.graphql.common.strategies.search import (
    # AddressSearchStrategy,
    AdjustmentSearchStrategy,
    CampaignSearchStrategy,
    CheckSearchStrategy,
    CompanySearchStrategy,
    ContactSearchStrategy,
    ContainerTypeSearchStrategy,
    CreditSearchStrategy,
    CustomerSearchStrategy,
    FactorySearchStrategy,
    FolderSearchStrategy,
    InvoiceSearchStrategy,
    JobSearchStrategy,
    NoteSearchStrategy,
    OrderAcknowledgementSearchStrategy,
    OrderSearchStrategy,
    PreOpportunitySearchStrategy,
    ProductSearchStrategy,
    QuoteSearchStrategy,
    ShippingCarrierSearchStrategy,
    SpecSheetSearchStrategy,
    TaskSearchStrategy,
    WarehouseSearchStrategy,
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
        InvoiceSearchStrategy(),
        OrderSearchStrategy(),
        CreditSearchStrategy(),
        CheckSearchStrategy(),
        AdjustmentSearchStrategy(),
        # AddressSearchStrategy(),
        ShippingCarrierSearchStrategy(),
        ContainerTypeSearchStrategy(),
        WarehouseSearchStrategy(),
        OrderAcknowledgementSearchStrategy(),
        FolderSearchStrategy(),
    ]

    for strategy in strategies:
        registry.register(strategy)

    return registry
