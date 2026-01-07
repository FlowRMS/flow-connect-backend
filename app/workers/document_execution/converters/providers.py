import aioinject

from app.graphql.invoices.services.order_detail_matcher import OrderDetailMatcherService

from .check_converter import CheckConverter
from .customer_converter import CustomerConverter
from .factory_converter import FactoryConverter
from .invoice_converter import InvoiceConverter
from .order_converter import OrderConverter
from .product_converter import ProductConverter
from .quote_converter import QuoteConverter
from .set_for_creation_service import SetForCreationService

converter_providers = [
    aioinject.Scoped(OrderConverter),
    aioinject.Scoped(CustomerConverter),
    aioinject.Scoped(FactoryConverter),
    aioinject.Scoped(ProductConverter),
    aioinject.Scoped(QuoteConverter),
    aioinject.Scoped(InvoiceConverter),
    aioinject.Scoped(CheckConverter),
    aioinject.Scoped(OrderDetailMatcherService),
    aioinject.Scoped(SetForCreationService),
]
