from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.checks.services.check_service import CheckService
from app.graphql.common.interfaces.bulk_delete_strategy import (
    BulkDeleteStrategyRegistry,
)
from app.graphql.common.strategies.bulk_delete import (
    CheckBulkDeleteStrategy,
    CustomerBulkDeleteStrategy,
    FactoryBulkDeleteStrategy,
    InvoiceBulkDeleteStrategy,
    OrderBulkDeleteStrategy,
    PreOpportunityBulkDeleteStrategy,
    ProductBulkDeleteStrategy,
    QuoteBulkDeleteStrategy,
)
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.orders.services.order_service import OrderService
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.products.services.product_service import ProductService


def create_bulk_delete_registry(
    factory_service: FactoryService,
    customer_service: CustomerService,
    product_service: ProductService,
    order_service: OrderService,
    invoice_service: InvoiceService,
    quote_service: QuoteService,
    check_service: CheckService,
    pre_opportunity_service: PreOpportunitiesService,
    session: AsyncSession,
) -> BulkDeleteStrategyRegistry:
    registry = BulkDeleteStrategyRegistry()

    strategies = [
        FactoryBulkDeleteStrategy(factory_service=factory_service, session=session),
        CustomerBulkDeleteStrategy(customer_service=customer_service, session=session),
        ProductBulkDeleteStrategy(product_service=product_service, session=session),
        OrderBulkDeleteStrategy(
            order_service=order_service,
            invoice_service=invoice_service,
            session=session,
        ),
        InvoiceBulkDeleteStrategy(invoice_service=invoice_service, session=session),
        QuoteBulkDeleteStrategy(quote_service=quote_service, session=session),
        CheckBulkDeleteStrategy(check_service=check_service, session=session),
        PreOpportunityBulkDeleteStrategy(
            pre_opportunity_service=pre_opportunity_service, session=session
        ),
    ]

    for strategy in strategies:
        registry.register(strategy)

    return registry
