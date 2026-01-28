"""Service for bulk product import from CSV."""

from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.products.product import Product
from commons.db.v6.core.products.product_quantity_pricing import ProductQuantityPricing
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.products.repositories.product_quantity_pricing_repository import (
    ProductQuantityPricingRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.strawberry.product_import_types import (
    ProductImportError,
    ProductImportInput,
    ProductImportItemInput,
    ProductImportResult,
)
from app.graphql.v2.core.products.strawberry.product_input import ProductInput


class ProductImportService:
    """Service for bulk importing products from normalized CSV data."""

    DEFAULT_COMMISSION_RATE = Decimal("0.10")
    MAX_QUANTITY_HIGH = Decimal("999999999")

    def __init__(
        self,
        session: AsyncSession,
        products_repository: ProductsRepository,
        quantity_pricing_repository: ProductQuantityPricingRepository,
    ) -> None:
        super().__init__()
        self.session = session
        self.products_repository = products_repository
        self.quantity_pricing_repository = quantity_pricing_repository

    async def import_products(
        self,
        import_input: ProductImportInput,
        default_uom_id: UUID,
    ) -> ProductImportResult:
        """
        Import products from normalized input data.

        This method handles:
        - Creating new products that don't exist
        - Updating existing products (by factory_part_number + factory_id)
        - Replacing quantity pricing bands for each product
        - NOT overwriting existing values with null/empty values
        """
        errors: list[ProductImportError] = []
        products_created = 0
        products_updated = 0
        quantity_pricing_created = 0

        factory_id = import_input.factory_id
        products_data = import_input.products

        if not products_data:
            return ProductImportResult(
                success=True,
                products_created=0,
                products_updated=0,
                quantity_pricing_created=0,
                errors=[],
                message="No products to import",
            )

        # Deduplicate products by factory_part_number (keep last occurrence)
        seen_fpn: dict[str, ProductImportItemInput] = {}
        for p in products_data:
            fpn = p.factory_part_number.strip() if p.factory_part_number else ""
            if fpn:
                seen_fpn[fpn] = p
        products_data = list(seen_fpn.values())
        logger.info(f"Importing {len(products_data)} unique products (after dedup)")

        if not products_data:
            return ProductImportResult(
                success=True,
                products_created=0,
                products_updated=0,
                quantity_pricing_created=0,
                errors=[],
                message="No products to import",
            )

        # Get existing products by factory_part_number
        fpn_factory_pairs = [(p.factory_part_number, factory_id) for p in products_data]
        existing_products = await self.products_repository.get_existing_products(
            fpn_factory_pairs
        )
        existing_by_fpn: dict[str, Product] = {
            p.factory_part_number: p for p in existing_products
        }

        # Separate into create vs update
        to_create: list[ProductImportItemInput] = []
        to_update: list[tuple[ProductImportItemInput, Product]] = []

        for product_data in products_data:
            existing = existing_by_fpn.get(product_data.factory_part_number)
            if existing:
                to_update.append((product_data, existing))
            else:
                to_create.append(product_data)

        # Create new products (may also update if duplicate found)
        if to_create:
            created_count, fallback_updated, create_errors = await self._create_products(
                to_create, factory_id, default_uom_id
            )
            products_created = created_count
            products_updated += fallback_updated  # Add fallback updates
            errors.extend(create_errors)

        # Update existing products
        if to_update:
            updated_count, update_errors = await self._update_products(to_update)
            products_updated += updated_count
            errors.extend(update_errors)

        # Handle quantity pricing for all products
        # First, get all products again (including newly created)
        all_fpn_pairs = [(p.factory_part_number, factory_id) for p in products_data]
        all_products = await self.products_repository.get_existing_products(
            all_fpn_pairs
        )
        products_by_fpn = {p.factory_part_number: p for p in all_products}

        for product_data in products_data:
            product = products_by_fpn.get(product_data.factory_part_number)
            if product and product_data.quantity_pricing:
                pricing_count = await self._replace_quantity_pricing(
                    product.id, product_data.quantity_pricing
                )
                quantity_pricing_created += pricing_count

        await self.session.flush()

        success = len(errors) == 0
        message = self._build_result_message(
            products_created, products_updated, quantity_pricing_created, len(errors)
        )

        return ProductImportResult(
            success=success,
            products_created=products_created,
            products_updated=products_updated,
            quantity_pricing_created=quantity_pricing_created,
            errors=errors,
            message=message,
        )

    async def _create_products(
        self,
        products_data: list[ProductImportItemInput],
        factory_id: UUID,
        default_uom_id: UUID,
    ) -> tuple[int, int, list[ProductImportError]]:
        """Create new products. Returns (created_count, updated_count, errors)."""
        errors: list[ProductImportError] = []
        created_count = 0
        updated_count = 0

        for product_data in products_data:
            try:
                # Use savepoint so we can recover from IntegrityError
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
                # Duplicate key - product already exists, try to update instead
                logger.info(
                    f"Product {product_data.factory_part_number} already exists, "
                    "updating instead"
                )
                try:
                    # Find the existing product and update it
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
                        # Shouldn't happen, but log it
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

    async def _update_products(
        self,
        products_to_update: list[tuple[ProductImportItemInput, Product]],
    ) -> tuple[int, list[ProductImportError]]:
        """Update existing products without overwriting with null values."""
        errors: list[ProductImportError] = []
        updated_count = 0

        for product_data, existing_product in products_to_update:
            try:
                # Only update non-null values
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

    async def _replace_quantity_pricing(
        self,
        product_id: UUID,
        quantity_pricing_data: list,
    ) -> int:
        """Replace all quantity pricing bands for a product."""
        # Delete existing quantity pricing for this product
        delete_stmt = delete(ProductQuantityPricing).where(
            ProductQuantityPricing.product_id == product_id
        )
        _ = await self.session.execute(delete_stmt)

        # Create new quantity pricing bands
        created_count = 0
        for band in quantity_pricing_data:
            quantity_high = (
                band.quantity_high
                if band.quantity_high is not None
                else self.MAX_QUANTITY_HIGH
            )

            pricing = ProductQuantityPricing(
                product_id=product_id,
                quantity_low=band.quantity_low,
                quantity_high=quantity_high,
                unit_price=band.unit_price,
            )
            self.session.add(pricing)
            created_count += 1

        return created_count

    def _build_result_message(
        self,
        created: int,
        updated: int,
        pricing: int,
        error_count: int,
    ) -> str:
        """Build a human-readable result message."""
        parts = []
        if created > 0:
            parts.append(f"{created} products created")
        if updated > 0:
            parts.append(f"{updated} products updated")
        if pricing > 0:
            parts.append(f"{pricing} quantity pricing bands created")
        if error_count > 0:
            parts.append(f"{error_count} errors")

        if not parts:
            return "No changes made"

        return ", ".join(parts)
