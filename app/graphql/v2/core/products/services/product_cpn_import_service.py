"""Service for bulk product CPN (Customer Part Number) import."""

from uuid import UUID

from commons.db.v6.core.customers.customer import Customer
from commons.db.v6.core.products.product import Product
from commons.db.v6.core.products.product_cpn import ProductCpn
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.products.repositories.product_cpn_repository import (
    ProductCpnRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.strawberry.product_cpn_import_types import (
    ProductCpnImportError,
    ProductCpnImportInput,
    ProductCpnImportItemInput,
    ProductCpnImportResult,
)


class ProductCpnImportService:
    """Service for bulk importing customer-specific pricing (CPNs)."""

    def __init__(
        self,
        session: AsyncSession,
        products_repository: ProductsRepository,
        cpn_repository: ProductCpnRepository,
    ) -> None:
        super().__init__()
        self.session = session
        self.products_repository = products_repository
        self.cpn_repository = cpn_repository

    async def import_cpns(
        self,
        import_input: ProductCpnImportInput,
    ) -> ProductCpnImportResult:
        """
        Import CPNs from normalized input data.

        This method handles:
        - Looking up products by factory_part_number + factory_id
        - Looking up customers by company_name
        - Creating new CPNs that don't exist
        - Updating existing CPNs (by product_id + customer_id)
        """
        errors: list[ProductCpnImportError] = []
        cpns_created = 0
        cpns_updated = 0

        factory_id = import_input.factory_id
        cpns_data = import_input.cpns

        if not cpns_data:
            return ProductCpnImportResult(
                success=True,
                cpns_created=0,
                cpns_updated=0,
                errors=[],
                message="No CPNs to import",
                products_not_found=[],
                customers_not_found=[],
            )

        # Deduplicate by (factory_part_number, customer_name) - keep last occurrence
        seen_keys: dict[tuple[str, str], ProductCpnImportItemInput] = {}
        for cpn in cpns_data:
            fpn = cpn.factory_part_number.strip() if cpn.factory_part_number else ""
            cname = cpn.customer_name.strip() if cpn.customer_name else ""
            if fpn and cname:
                seen_keys[(fpn, cname)] = cpn
        cpns_data = list(seen_keys.values())
        logger.info(f"Importing {len(cpns_data)} unique CPNs (after dedup)")

        if not cpns_data:
            return ProductCpnImportResult(
                success=True,
                cpns_created=0,
                cpns_updated=0,
                errors=[],
                message="No CPNs to import",
                products_not_found=[],
                customers_not_found=[],
            )

        # Step 1: Lookup products by factory_part_number
        unique_fpns = list(set(c.factory_part_number.strip() for c in cpns_data))
        fpn_factory_pairs = [(fpn, factory_id) for fpn in unique_fpns]
        existing_products = await self.products_repository.get_existing_products(
            fpn_factory_pairs
        )
        products_by_fpn: dict[str, Product] = {
            p.factory_part_number: p for p in existing_products
        }
        products_not_found = [fpn for fpn in unique_fpns if fpn not in products_by_fpn]
        if products_not_found:
            logger.warning(f"Products not found: {products_not_found[:10]}...")

        # Step 2: Lookup customers by company_name
        unique_customer_names = list(set(c.customer_name.strip() for c in cpns_data))
        customers_by_name = await self._get_customers_by_name(unique_customer_names)
        customers_not_found = [
            name for name in unique_customer_names if name not in customers_by_name
        ]
        if customers_not_found:
            logger.warning(f"Customers not found: {customers_not_found[:10]}...")

        # Step 3: Build resolved CPN data
        resolved_cpns: list[tuple[ProductCpnImportItemInput, UUID, UUID]] = []
        for cpn_data in cpns_data:
            fpn = cpn_data.factory_part_number.strip()
            cname = cpn_data.customer_name.strip()

            product = products_by_fpn.get(fpn)
            customer = customers_by_name.get(cname)

            if not product:
                errors.append(
                    ProductCpnImportError(
                        factory_part_number=fpn,
                        customer_name=cname,
                        error=f"Product not found: {fpn}",
                    )
                )
                continue

            if not customer:
                errors.append(
                    ProductCpnImportError(
                        factory_part_number=fpn,
                        customer_name=cname,
                        error=f"Customer not found: {cname}",
                    )
                )
                continue

            resolved_cpns.append((cpn_data, product.id, customer.id))

        # Step 4: Get existing CPNs for upsert logic
        product_customer_pairs = [(pid, cid) for _, pid, cid in resolved_cpns]
        existing_cpns = await self.cpn_repository.find_existing_cpns(
            product_customer_pairs
        )

        # Step 5: Process each resolved CPN
        for cpn_data, product_id, customer_id in resolved_cpns:
            existing_cpn = existing_cpns.get((product_id, customer_id))
            fpn = cpn_data.factory_part_number.strip()
            cname = cpn_data.customer_name.strip()

            try:
                if existing_cpn:
                    # Update existing CPN
                    existing_cpn.customer_part_number = cpn_data.customer_part_number
                    existing_cpn.unit_price = cpn_data.unit_price
                    existing_cpn.commission_rate = cpn_data.commission_rate
                    cpns_updated += 1
                else:
                    # Create new CPN with savepoint for IntegrityError handling
                    try:
                        async with self.session.begin_nested():
                            new_cpn = ProductCpn(
                                customer_id=customer_id,
                                customer_part_number=cpn_data.customer_part_number,
                                unit_price=cpn_data.unit_price,
                                commission_rate=cpn_data.commission_rate,
                            )
                            new_cpn.product_id = product_id
                            self.session.add(new_cpn)
                            cpns_created += 1
                    except IntegrityError:
                        # Race condition - CPN was created between check and insert
                        logger.info(
                            f"CPN for {fpn}/{cname} already exists, updating instead"
                        )
                        stmt = select(ProductCpn).where(
                            ProductCpn.product_id == product_id,
                            ProductCpn.customer_id == customer_id,
                        )
                        result = await self.session.execute(stmt)
                        existing = result.scalar_one_or_none()
                        if existing:
                            existing.customer_part_number = (
                                cpn_data.customer_part_number
                            )
                            existing.unit_price = cpn_data.unit_price
                            existing.commission_rate = cpn_data.commission_rate
                            cpns_updated += 1
                        else:
                            errors.append(
                                ProductCpnImportError(
                                    factory_part_number=fpn,
                                    customer_name=cname,
                                    error="IntegrityError but CPN not found",
                                )
                            )
            except Exception as e:
                logger.error(f"Failed to process CPN {fpn}/{cname}: {e}")
                errors.append(
                    ProductCpnImportError(
                        factory_part_number=fpn,
                        customer_name=cname,
                        error=str(e),
                    )
                )

        await self.session.flush()

        success = len(errors) == 0
        message = self._build_result_message(
            cpns_created,
            cpns_updated,
            len(errors),
            len(products_not_found),
            len(customers_not_found),
        )

        return ProductCpnImportResult(
            success=success,
            cpns_created=cpns_created,
            cpns_updated=cpns_updated,
            errors=errors,
            message=message,
            products_not_found=products_not_found,
            customers_not_found=customers_not_found,
        )

    async def _get_customers_by_name(
        self, company_names: list[str]
    ) -> dict[str, Customer]:
        """Look up customers by company name (exact match)."""
        if not company_names:
            return {}

        stmt = select(Customer).where(Customer.company_name.in_(company_names))
        result = await self.session.execute(stmt)
        customers = result.scalars().all()
        return {c.company_name: c for c in customers}

    def _build_result_message(
        self,
        created: int,
        updated: int,
        error_count: int,
        products_not_found: int,
        customers_not_found: int,
    ) -> str:
        """Build a human-readable result message."""
        parts = []
        if created > 0:
            parts.append(f"{created} CPNs created")
        if updated > 0:
            parts.append(f"{updated} CPNs updated")
        if error_count > 0:
            parts.append(f"{error_count} errors")
        if products_not_found > 0:
            parts.append(f"{products_not_found} products not found")
        if customers_not_found > 0:
            parts.append(f"{customers_not_found} customers not found")

        if not parts:
            return "No changes made"

        return ", ".join(parts)
