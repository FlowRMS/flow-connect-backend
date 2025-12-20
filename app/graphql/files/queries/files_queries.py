from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.customers.strawberry.customer_response import CustomerResponse
from app.graphql.factories.strawberry.factory_response import FactoryResponse
from app.graphql.files.services.files_service import FilesService
from app.graphql.files.strawberry.file_linked_entities_response import (
    FileLinkedEntitiesResponse,
)
from app.graphql.inject import inject
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.orders.strawberry.order_response import OrderResponse
from app.graphql.products.strawberry.product_response import ProductResponse
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


@strawberry.type
class FilesQueries:
    @strawberry.field
    @inject
    async def file_linked_entities(
        self,
        file_id: UUID,
        service: Injected[FilesService],
    ) -> FileLinkedEntitiesResponse:
        quotes = await service.get_linked_quotes(file_id)
        orders = await service.get_linked_orders(file_id)
        invoices = await service.get_linked_invoices(file_id)
        checks = await service.get_linked_checks(file_id)
        customers = await service.get_linked_customers(file_id)
        factories = await service.get_linked_factories(file_id)
        products = await service.get_linked_products(file_id)

        return FileLinkedEntitiesResponse(
            quotes=QuoteResponse.from_orm_model_list(quotes),
            orders=OrderResponse.from_orm_model_list(orders),
            invoices=InvoiceResponse.from_orm_model_list(invoices),
            checks=CheckResponse.from_orm_model_list(checks),
            customers=CustomerResponse.from_orm_model_list(customers),
            factories=FactoryResponse.from_orm_model_list(factories),
            products=ProductResponse.from_orm_model_list(products),
        )
