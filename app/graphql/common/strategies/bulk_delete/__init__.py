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
from app.graphql.common.strategies.bulk_delete.product_bulk_delete_strategy import (
    ProductBulkDeleteStrategy,
)

__all__ = [
    "CustomerBulkDeleteStrategy",
    "FactoryBulkDeleteStrategy",
    "InvoiceBulkDeleteStrategy",
    "OrderBulkDeleteStrategy",
    "ProductBulkDeleteStrategy",
]
