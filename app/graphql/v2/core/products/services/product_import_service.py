from uuid import UUID

from commons.db.v6.core.products.product import Product
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.customers.repositories.customers_repository import (
    CustomersRepository,
)
from app.graphql.v2.core.products.repositories.product_cpn_repository import (
    ProductCpnRepository,
)
from app.graphql.v2.core.products.repositories.product_quantity_pricing_repository import (
    ProductQuantityPricingRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.services.product_import_operations import (
    ProductImportOperations,
)
from app.graphql.v2.core.products.services.product_pricing_operations import (
    ProductPricingOperations,
)
from app.graphql.v2.core.products.strawberry.product_import_types import (
    ProductImportError,
    ProductImportInput,
    ProductImportItemInput,
    ProductImportResult,
)


class ProductImportService:
    def __init__(
        self,
        session: AsyncSession,
        products_repository: ProductsRepository,
        quantity_pricing_repository: ProductQuantityPricingRepository,
        customers_repository: CustomersRepository,
        cpn_repository: ProductCpnRepository,
    ) -> None:
        super().__init__()
        self.session = session
        self.products_repository = products_repository
        self.quantity_pricing_repository = quantity_pricing_repository
        self.customers_repository = customers_repository
        self.cpn_repository = cpn_repository
        self._import_ops = ProductImportOperations(session, products_repository)
        self._pricing_ops = ProductPricingOperations(
            session, customers_repository, cpn_repository
        )

    async def import_products(
        self,
        import_input: ProductImportInput,
        default_uom_id: UUID,
    ) -> ProductImportResult:
        errors: list[ProductImportError] = []
        products_created = 0
        products_updated = 0
        quantity_pricing_created = 0
        customer_pricing_created = 0
        customer_pricing_updated = 0
        customers_not_found: list[str] = []

        factory_id = import_input.factory_id
        products_data = import_input.products

        if not products_data:
            return self._empty_result("No products to import")

        products_data = self._deduplicate_products(products_data)
        logger.info(f"Importing {len(products_data)} unique products (after dedup)")

        if not products_data:
            return self._empty_result("No products to import")

        existing_by_fpn = await self._get_existing_products_map(
            products_data, factory_id
        )
        to_create, to_update = self._separate_create_update(
            products_data, existing_by_fpn
        )

        if to_create:
            (
                created,
                fallback_updated,
                create_errors,
            ) = await self._import_ops.create_products(
                to_create, factory_id, default_uom_id
            )
            products_created = created
            products_updated += fallback_updated
            errors.extend(create_errors)

        if to_update:
            updated, update_errors = await self._import_ops.update_products(to_update)
            products_updated += updated
            errors.extend(update_errors)

        products_by_fpn = await self._get_existing_products_map(
            products_data, factory_id
        )

        for product_data in products_data:
            product = products_by_fpn.get(product_data.factory_part_number)
            if product and product_data.quantity_pricing:
                pricing_count = await self._pricing_ops.replace_quantity_pricing(
                    product.id, product_data.quantity_pricing
                )
                quantity_pricing_created += pricing_count

        all_customer_names = self._collect_customer_names(products_data)

        if all_customer_names:
            customers_by_name = await self._pricing_ops.get_customers_by_name(
                list(all_customer_names)
            )
            customers_not_found = [
                name for name in all_customer_names if name not in customers_by_name
            ]
            if customers_not_found:
                logger.warning(f"Customers not found: {customers_not_found[:10]}...")

            if self.cpn_repository:
                for product_data in products_data:
                    product = products_by_fpn.get(product_data.factory_part_number)
                    if product and product_data.customer_pricing:
                        (
                            created,
                            updated,
                            cpn_errors,
                        ) = await self._pricing_ops.process_customer_pricing(
                            product.id,
                            product_data.factory_part_number,
                            product_data.customer_pricing,
                            customers_by_name,
                        )
                        customer_pricing_created += created
                        customer_pricing_updated += updated
                        errors.extend(cpn_errors)

        await self.session.flush()

        return ProductImportResult(
            success=len(errors) == 0,
            products_created=products_created,
            products_updated=products_updated,
            quantity_pricing_created=quantity_pricing_created,
            customer_pricing_created=customer_pricing_created,
            customer_pricing_updated=customer_pricing_updated,
            errors=errors,
            message=self._build_result_message(
                products_created,
                products_updated,
                quantity_pricing_created,
                customer_pricing_created,
                customer_pricing_updated,
                len(errors),
            ),
            customers_not_found=customers_not_found,
        )

    def _deduplicate_products(
        self, products_data: list[ProductImportItemInput]
    ) -> list[ProductImportItemInput]:
        seen_fpn: dict[str, ProductImportItemInput] = {}
        for p in products_data:
            fpn = p.factory_part_number.strip() if p.factory_part_number else ""
            if fpn:
                seen_fpn[fpn] = p
        return list(seen_fpn.values())

    async def _get_existing_products_map(
        self,
        products_data: list[ProductImportItemInput],
        factory_id: UUID,
    ) -> dict[str, Product]:
        fpn_factory_pairs = [(p.factory_part_number, factory_id) for p in products_data]
        existing_products = await self.products_repository.get_existing_products(
            fpn_factory_pairs
        )
        return {p.factory_part_number: p for p in existing_products}

    def _separate_create_update(
        self,
        products_data: list[ProductImportItemInput],
        existing_by_fpn: dict[str, Product],
    ) -> tuple[
        list[ProductImportItemInput], list[tuple[ProductImportItemInput, Product]]
    ]:
        to_create: list[ProductImportItemInput] = []
        to_update: list[tuple[ProductImportItemInput, Product]] = []

        for product_data in products_data:
            existing = existing_by_fpn.get(product_data.factory_part_number)
            if existing:
                to_update.append((product_data, existing))
            else:
                to_create.append(product_data)

        return to_create, to_update

    def _collect_customer_names(
        self, products_data: list[ProductImportItemInput]
    ) -> set[str]:
        all_customer_names: set[str] = set()
        for product_data in products_data:
            if product_data.customer_pricing:
                for cp in product_data.customer_pricing:
                    if cp.customer_name:
                        all_customer_names.add(cp.customer_name.strip())
        return all_customer_names

    def _empty_result(self, message: str) -> ProductImportResult:
        return ProductImportResult(
            success=True,
            products_created=0,
            products_updated=0,
            quantity_pricing_created=0,
            customer_pricing_created=0,
            customer_pricing_updated=0,
            errors=[],
            message=message,
            customers_not_found=[],
        )

    def _build_result_message(
        self,
        created: int,
        updated: int,
        qty_pricing: int,
        cpn_created: int,
        cpn_updated: int,
        error_count: int,
    ) -> str:
        parts = []
        if created > 0:
            parts.append(f"{created} products created")
        if updated > 0:
            parts.append(f"{updated} products updated")
        if qty_pricing > 0:
            parts.append(f"{qty_pricing} quantity pricing bands created")
        if cpn_created > 0:
            parts.append(f"{cpn_created} customer prices created")
        if cpn_updated > 0:
            parts.append(f"{cpn_updated} customer prices updated")
        if error_count > 0:
            parts.append(f"{error_count} errors")

        if not parts:
            return "No changes made"

        return ", ".join(parts)
