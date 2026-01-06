import aioinject

from app.graphql.invoices.services.order_detail_matcher import OrderDetailMatcherService

from .customer_converter import CustomerConverter
from .delivery_converter import DeliveryConverter
from .factory_converter import FactoryConverter
from .invoice_converter import InvoiceConverter
from .order_converter import OrderConverter
from .product_converter import ProductConverter
from .quote_converter import QuoteConverter

converter_providers = [
    aioinject.Scoped(OrderConverter),
    aioinject.Scoped(CustomerConverter),
    aioinject.Scoped(DeliveryConverter),
    aioinject.Scoped(FactoryConverter),
    aioinject.Scoped(ProductConverter),
    aioinject.Scoped(QuoteConverter),
    aioinject.Scoped(InvoiceConverter),
    aioinject.Scoped(OrderDetailMatcherService),
]
