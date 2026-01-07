from app.graphql.checks.services.check_service import CheckService
from app.graphql.common.interfaces.entity_lookup_strategy import (
    EntityLookupStrategyRegistry,
)
from app.graphql.common.strategies.entity_lookup import (
    CheckEntityStrategy,
    InvoiceEntityStrategy,
    OrderEntityStrategy,
    PreOpportunityEntityStrategy,
    QuoteEntityStrategy,
)
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.orders.services.order_service import OrderService
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.quotes.services.quote_service import QuoteService


def create_entity_lookup_registry(
    pre_opportunities_service: PreOpportunitiesService,
    quote_service: QuoteService,
    order_service: OrderService,
    invoice_service: InvoiceService,
    check_service: CheckService,
) -> EntityLookupStrategyRegistry:
    registry = EntityLookupStrategyRegistry()

    strategies = [
        PreOpportunityEntityStrategy(service=pre_opportunities_service),
        QuoteEntityStrategy(service=quote_service),
        OrderEntityStrategy(service=order_service),
        InvoiceEntityStrategy(service=invoice_service),
        CheckEntityStrategy(service=check_service),
    ]

    for strategy in strategies:
        registry.register(strategy)

    return registry
