from app.graphql.common.strategies.bulk_delete.check_bulk_delete_strategy import (
    CheckBulkDeleteStrategy,
)
from app.graphql.common.strategies.bulk_delete.customer_bulk_delete_strategy import (
    CustomerBulkDeleteStrategy,
)
from app.graphql.common.strategies.bulk_delete.factory_bulk_delete_strategy import (
    FactoryBulkDeleteStrategy,
)
from app.graphql.common.strategies.bulk_delete.invoice_bulk_delete_strategy import (
    InvoiceBulkDeleteStrategy,
)
from app.graphql.common.strategies.bulk_delete.order_bulk_delete_strategy import (
    OrderBulkDeleteStrategy,
)
from app.graphql.common.strategies.bulk_delete.pre_opportunity_bulk_delete_strategy import (
    PreOpportunityBulkDeleteStrategy,
)
from app.graphql.common.strategies.bulk_delete.product_bulk_delete_strategy import (
    ProductBulkDeleteStrategy,
)
from app.graphql.common.strategies.bulk_delete.quote_bulk_delete_strategy import (
    QuoteBulkDeleteStrategy,
)

__all__ = [
    "CheckBulkDeleteStrategy",
    "CustomerBulkDeleteStrategy",
    "FactoryBulkDeleteStrategy",
    "InvoiceBulkDeleteStrategy",
    "OrderBulkDeleteStrategy",
    "PreOpportunityBulkDeleteStrategy",
    "ProductBulkDeleteStrategy",
    "QuoteBulkDeleteStrategy",
]
