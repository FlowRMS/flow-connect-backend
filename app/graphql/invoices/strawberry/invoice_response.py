from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Invoice
from commons.db.v6.commission.invoices.invoice import InvoiceStatus
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.invoices.strawberry.invoice_balance_response import (
    InvoiceBalanceResponse,
)
from app.graphql.invoices.strawberry.invoice_detail_response import (
    InvoiceDetailResponse,
)
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class InvoiceLiteResponse(DTOMixin[Invoice]):
    _instance: strawberry.Private[Invoice]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    invoice_number: str
    entity_date: date
    due_date: date | None
    order_id: UUID
    status: InvoiceStatus
    published: bool
    locked: bool
    creation_type: CreationType
    balance_id: UUID

    @classmethod
    def from_orm_model(cls, model: Invoice) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            invoice_number=model.invoice_number,
            entity_date=model.entity_date,
            due_date=model.due_date,
            order_id=model.order_id,
            status=model.status,
            published=model.published,
            locked=model.locked,
            creation_type=model.creation_type,
            balance_id=model.balance_id,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/invoices/list/{self.id}"


@strawberry.type
class InvoiceCheckResponse(InvoiceLiteResponse):
    @strawberry.field
    def order(self) -> OrderLiteResponse:
        return OrderLiteResponse.from_orm_model(self._instance.order)


@strawberry.type
class InvoiceResponse(InvoiceCheckResponse):
    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def balance(self) -> InvoiceBalanceResponse:
        return InvoiceBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[InvoiceDetailResponse]:
        return InvoiceDetailResponse.from_orm_model_list(self._instance.details)
