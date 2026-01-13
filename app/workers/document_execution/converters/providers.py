import aioinject

from app.graphql.invoices.services.order_detail_matcher import OrderDetailMatcherService

from .adjustment_converter import AdjustmentConverter
from .adjustment_creation_handler import AdjustmentCreationHandler
from .check_converter import CheckConverter
from .credit_converter import CreditConverter
from .credit_creation_handler import CreditCreationHandler
from .customer_converter import CustomerConverter
from .delivery_converter import DeliveryConverter
from .factory_converter import FactoryConverter
from .invoice_converter import InvoiceConverter
from .invoice_creation_handler import InvoiceCreationHandler
from .order_converter import OrderConverter
from .order_creation_handler import OrderCreationHandler
from .product_converter import ProductConverter
from .quote_converter import QuoteConverter
from .set_for_creation_service import SetForCreationService

converter_providers = [
    aioinject.Scoped(OrderConverter),
    aioinject.Scoped(CustomerConverter),
    aioinject.Scoped(DeliveryConverter),
    aioinject.Scoped(FactoryConverter),
    aioinject.Scoped(ProductConverter),
    aioinject.Scoped(QuoteConverter),
    aioinject.Scoped(InvoiceConverter),
    aioinject.Scoped(CreditConverter),
    aioinject.Scoped(AdjustmentConverter),
    aioinject.Scoped(CheckConverter),
    aioinject.Scoped(OrderDetailMatcherService),
    aioinject.Scoped(OrderCreationHandler),
    aioinject.Scoped(InvoiceCreationHandler),
    aioinject.Scoped(CreditCreationHandler),
    aioinject.Scoped(AdjustmentCreationHandler),
    aioinject.Scoped(SetForCreationService),
]
