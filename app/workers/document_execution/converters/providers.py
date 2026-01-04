import aioinject

from .order_converter import OrderConverter

converter_providers = [
    aioinject.Scoped(OrderConverter),
]
