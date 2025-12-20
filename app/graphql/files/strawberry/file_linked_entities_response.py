import strawberry

from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.orders.strawberry.order_response import OrderResponse
from app.graphql.quotes.strawberry.quote_response import QuoteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import CustomerResponse
from app.graphql.v2.core.factories.strawberry.factory_response import FactoryResponse
from app.graphql.v2.core.products.strawberry.product_response import ProductResponse


@strawberry.type
class FileLinkedEntitiesResponse:
    quotes: list[QuoteResponse]
    orders: list[OrderResponse]
    invoices: list[InvoiceResponse]
    checks: list[CheckResponse]
    customers: list[CustomerResponse]
    factories: list[FactoryResponse]
    products: list[ProductResponse]
