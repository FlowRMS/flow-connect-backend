from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.customers.customer_factory_sales_rep import (
    CustomerFactorySalesRep,
)

from app.errors.common_errors import NotFoundError, ValidationError
from app.graphql.v2.core.customers.repositories.customer_factory_sales_rep_repository import (
    CustomerFactorySalesRepRepository,
)
from app.graphql.v2.core.customers.strawberry.customer_factory_sales_rep_input import (
    CustomerFactorySalesRepInput,
)


class CustomerFactorySalesRepService:
    def __init__(self, repository: CustomerFactorySalesRepRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, rep_id: UUID) -> CustomerFactorySalesRep:
        rep = await self.repository.get_by_id_with_relations(rep_id)
        if not rep:
            raise NotFoundError(f"CustomerFactorySalesRep with id {rep_id} not found")
        return rep

    async def list_by_customer_and_factory(
        self,
        customer_id: UUID,
        factory_id: UUID,
    ) -> list[CustomerFactorySalesRep]:
        return await self.repository.list_by_customer_and_factory(
            customer_id, factory_id
        )

    async def create(
        self,
        rep_input: CustomerFactorySalesRepInput,
    ) -> CustomerFactorySalesRep:
        await self._validate_rates_sum(
            customer_id=rep_input.customer_id,
            factory_id=rep_input.factory_id,
            new_rate=rep_input.rate,
            exclude_id=None,
        )
        rep = await self.repository.create(rep_input.to_orm_model())
        return await self.get_by_id(rep.id)

    async def update(
        self,
        rep_id: UUID,
        rep_input: CustomerFactorySalesRepInput,
    ) -> CustomerFactorySalesRep:
        existing = await self.repository.get_by_id(rep_id)
        if not existing:
            raise NotFoundError(f"CustomerFactorySalesRep with id {rep_id} not found")

        await self._validate_rates_sum(
            customer_id=rep_input.customer_id,
            factory_id=rep_input.factory_id,
            new_rate=rep_input.rate,
            exclude_id=rep_id,
        )

        rep = rep_input.to_orm_model()
        rep.id = rep_id
        _ = await self.repository.update(rep)
        return await self.get_by_id(rep_id)

    async def delete(self, rep_id: UUID) -> bool:
        if not await self.repository.exists(rep_id):
            raise NotFoundError(f"CustomerFactorySalesRep with id {rep_id} not found")
        return await self.repository.delete(rep_id)

    async def _validate_rates_sum(
        self,
        customer_id: UUID,
        factory_id: UUID,
        new_rate: Decimal,
        exclude_id: UUID | None,
    ) -> None:
        """
        Validates that total rates for a customer+factory combo sum to 100%.
        This is called before create/update to ensure the operation would not
        violate the constraint.
        """
        existing_reps = await self.repository.list_by_customer_and_factory(
            customer_id, factory_id
        )

        total = new_rate
        for rep in existing_reps:
            if exclude_id and rep.id == exclude_id:
                continue
            total += rep.rate

        if total != Decimal("100"):
            raise ValidationError(
                f"Total rates for customer and factory must equal 100%. "
                f"Current total would be: {total}%"
            )
