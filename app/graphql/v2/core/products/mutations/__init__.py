from app.graphql.v2.core.products.mutations.product_category_mutations import (
    ProductCategoryMutations,
)
from app.graphql.v2.core.products.mutations.product_cpn_mutations import (
    ProductCpnMutations,
)
from app.graphql.v2.core.products.mutations.product_import_mutations import (
    ProductImportMutations,
)
from app.graphql.v2.core.products.mutations.product_quantity_pricing_mutations import (
    ProductQuantityPricingMutations,
)
from app.graphql.v2.core.products.mutations.product_uom_mutations import (
    ProductUomMutations,
)
from app.graphql.v2.core.products.mutations.products_mutations import ProductsMutations

__all__ = [
    "ProductsMutations",
    "ProductUomMutations",
    "ProductCategoryMutations",
    "ProductCpnMutations",
    "ProductQuantityPricingMutations",
    "ProductImportMutations",
]
