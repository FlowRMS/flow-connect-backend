from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.customers.customer import Customer
from commons.db.v6.core.products.product_cpn import ProductCpn
from commons.db.v6.core.products.product_quantity_pricing import ProductQuantityPricing
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.graphql.v2.core.customers.repositories.customers_repository import (
    CustomersRepository,
)
from app.graphql.v2.core.products.repositories.product_cpn_repository import (
    ProductCpnRepository,
)
from app.graphql.v2.core.products.repositories.product_quantity_pricing_repository import (
    ProductQuantityPricingRepository,
)
from app.graphql.v2.core.products.strawberry.customer_pricing_import_input import (
    CustomerPricingImportInput,
)
from app.graphql.v2.core.products.strawberry.product_import_error import (
    ProductImportError,
)
from app.graphql.v2.core.products.strawberry.quantity_pricing_import_input import (
    QuantityPricingImportInput,
)


class ProductPricingOperations:
    MAX_QUANTITY_HIGH = Decimal("999999999")

    def __init__(
        self,
        customers_repository: CustomersRepository,
        cpn_repository: ProductCpnRepository,
        quantity_pricing_repository: ProductQuantityPricingRepository,
    ) -> None:
        super().__init__()
        self.customers_repository = customers_repository
        self.cpn_repository = cpn_repository
        self.quantity_pricing_repository = quantity_pricing_repository

    async def replace_quantity_pricing(
        self,
        product_id: UUID,
        quantity_pricing_data: list[QuantityPricingImportInput],
    ) -> int:
        await self.quantity_pricing_repository.delete_by_product_id(product_id)

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
            await self.quantity_pricing_repository.add_pricing(pricing)
            created_count += 1

        return created_count

    async def get_customers_by_name(
        self, company_names: list[str]
    ) -> dict[str, Customer]:
        return await self.customers_repository.get_by_company_names(company_names)

    async def process_customer_pricing(
        self,
        product_id: UUID,
        factory_part_number: str,
        customer_pricing_data: list[CustomerPricingImportInput],
        customers_by_name: dict[str, Customer],
    ) -> tuple[int, int, list[ProductImportError]]:
        errors: list[ProductImportError] = []
        created_count = 0
        updated_count = 0

        resolved_cpns: list[tuple[UUID, CustomerPricingImportInput]] = []
        for cp_data in customer_pricing_data:
            customer_name = (
                cp_data.customer_name.strip() if cp_data.customer_name else ""
            )
            customer = customers_by_name.get(customer_name)
            if not customer:
                continue
            resolved_cpns.append((customer.id, cp_data))

        if not resolved_cpns:
            return 0, 0, []

        product_customer_pairs = [(product_id, cid) for cid, _ in resolved_cpns]
        existing_cpns = await self.cpn_repository.find_existing_cpns(
            product_customer_pairs
        )

        for customer_id, cp_data in resolved_cpns:
            existing_cpn = existing_cpns.get((product_id, customer_id))
            customer_name = cp_data.customer_name.strip()

            try:
                if existing_cpn:
                    if cp_data.customer_part_number is not None:
                        existing_cpn.customer_part_number = cp_data.customer_part_number
                    existing_cpn.unit_price = cp_data.unit_price
                    existing_cpn.commission_rate = cp_data.commission_rate
                    updated_count += 1
                else:
                    try:
                        new_cpn = ProductCpn(
                            customer_id=customer_id,
                            customer_part_number=cp_data.customer_part_number or "",
                            unit_price=cp_data.unit_price,
                            commission_rate=cp_data.commission_rate,
                        )
                        new_cpn.product_id = product_id
                        _ = await self.cpn_repository.create_with_savepoint(new_cpn)
                        created_count += 1
                    except IntegrityError:
                        logger.info(
                            f"CPN for {factory_part_number}/{customer_name} exists, updating"
                        )
                        existing = (
                            await self.cpn_repository.find_cpn_by_product_and_customer(
                                product_id, customer_id
                            )
                        )
                        if existing:
                            if cp_data.customer_part_number is not None:
                                existing.customer_part_number = (
                                    cp_data.customer_part_number
                                )
                            existing.unit_price = cp_data.unit_price
                            existing.commission_rate = cp_data.commission_rate
                            updated_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to process CPN {factory_part_number}/{customer_name}: {e}"
                )
                errors.append(
                    ProductImportError(
                        factory_part_number=factory_part_number,
                        error=f"CPN error for {customer_name}: {e}",
                    )
                )

        return created_count, updated_count, errors
