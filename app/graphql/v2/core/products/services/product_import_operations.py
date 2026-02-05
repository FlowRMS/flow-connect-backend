from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.products.product import Product
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.strawberry.product_import_error import (
    ProductImportError,
)
from app.graphql.v2.core.products.strawberry.product_import_item_input import (
    ProductImportItemInput,
)
from app.graphql.v2.core.products.strawberry.product_input import ProductInput


class ProductImportOperations:
    DEFAULT_COMMISSION_RATE = Decimal("0.10")

    def __init__(
        self,
        session: AsyncSession,
        products_repository: ProductsRepository,
    ) -> None:
        super().__init__()
        self.session = session
        self.products_repository = products_repository

    async def create_products(
        self,
        products_data: list[ProductImportItemInput],
        factory_id: UUID,
        default_uom_id: UUID,
    ) -> tuple[int, int, list[ProductImportError]]:
        errors: list[ProductImportError] = []
        created_count = 0
        updated_count = 0

        for product_data in products_data:
            try:
                async with self.session.begin_nested():
                    product_input = ProductInput(
                        factory_part_number=product_data.factory_part_number,
                        factory_id=factory_id,
                        unit_price=product_data.unit_price,
                        default_commission_rate=(
                            product_data.default_commission_rate
                            or self.DEFAULT_COMMISSION_RATE
                        ),
                        product_uom_id=default_uom_id,
                        description=product_data.description,
                        upc=product_data.upc,
                        published=True,
                    )
                    _ = await self.products_repository.create(
                        product_input.to_orm_model()
                    )
                    created_count += 1
            except IntegrityError as e:
                logger.info(
                    f"Product {product_data.factory_part_number} already exists, "
                    "updating instead"
                )
                try:
                    stmt = select(Product).where(
                        Product.factory_part_number == product_data.factory_part_number,
                        Product.factory_id == factory_id,
                    )
                    result = await self.session.execute(stmt)
                    existing = result.scalar_one_or_none()

                    if existing:
                        existing.unit_price = product_data.unit_price
                        if product_data.description is not None:
                            existing.description = product_data.description
                        if product_data.upc is not None:
                            existing.upc = product_data.upc
                        if product_data.default_commission_rate is not None:
                            existing.default_commission_rate = (
                                product_data.default_commission_rate
                            )
                        updated_count += 1
                    else:
                        logger.warning(
                            f"IntegrityError but product not found: "
                            f"{product_data.factory_part_number}"
                        )
                        errors.append(
                            ProductImportError(
                                factory_part_number=product_data.factory_part_number,
                                error=str(e),
                            )
                        )
                except Exception as update_error:
                    logger.error(
                        f"Failed to update product {product_data.factory_part_number}: "
                        f"{update_error}"
                    )
                    errors.append(
                        ProductImportError(
                            factory_part_number=product_data.factory_part_number,
                            error=str(update_error),
                        )
                    )
            except Exception as e:
                logger.error(
                    f"Failed to create product {product_data.factory_part_number}: {e}"
                )
                errors.append(
                    ProductImportError(
                        factory_part_number=product_data.factory_part_number,
                        error=str(e),
                    )
                )

        return created_count, updated_count, errors

    async def update_products(
        self,
        products_to_update: list[tuple[ProductImportItemInput, Product]],
    ) -> tuple[int, list[ProductImportError]]:
        errors: list[ProductImportError] = []
        updated_count = 0

        for product_data, existing_product in products_to_update:
            try:
                existing_product.unit_price = product_data.unit_price

                if product_data.description is not None:
                    existing_product.description = product_data.description

                if product_data.upc is not None:
                    existing_product.upc = product_data.upc

                if product_data.default_commission_rate is not None:
                    existing_product.default_commission_rate = (
                        product_data.default_commission_rate
                    )

                updated_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to update product {product_data.factory_part_number}: {e}"
                )
                errors.append(
                    ProductImportError(
                        factory_part_number=product_data.factory_part_number,
                        error=str(e),
                    )
                )

        await self.session.flush()
        return updated_count, errors
