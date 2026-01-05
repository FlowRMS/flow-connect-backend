import aioinject

from .customer_converter import CustomerConverter
from .factory_converter import FactoryConverter
from .order_converter import OrderConverter
from .product_converter import ProductConverter
from .quote_converter import QuoteConverter

converter_providers = [
    aioinject.Scoped(OrderConverter),
    aioinject.Scoped(CustomerConverter),
    aioinject.Scoped(FactoryConverter),
    aioinject.Scoped(ProductConverter),
    aioinject.Scoped(QuoteConverter),
]
