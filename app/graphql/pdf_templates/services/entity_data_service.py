

import logging
from datetime import date, datetime
from typing import Any
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.models import Check, Invoice, Order, Quote

from app.errors.common_errors import NotFoundError
from app.graphql.invoices.repositories.invoices_repository import InvoicesRepository
from app.graphql.orders.repositories.orders_repository import OrdersRepository
from app.graphql.quotes.repositories.quotes_repository import QuotesRepository
from app.graphql.checks.repositories.checks_repository import ChecksRepository
from app.graphql.pre_opportunities.repositories.pre_opportunities_repository import (
    PreOpportunitiesRepository,
)
from app.graphql.pre_opportunities.models.pre_opportunity_model import (
    PreOpportunity,
)
from app.graphql.pre_opportunities.models.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)

logger = logging.getLogger(__name__)


class EntityDataService:


    def __init__(
        self,
        orders_repository: OrdersRepository,
        invoices_repository: InvoicesRepository,
        quotes_repository: QuotesRepository,
        checks_repository: ChecksRepository,
        pre_opportunities_repository: PreOpportunitiesRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.orders_repository = orders_repository
        self.invoices_repository = invoices_repository
        self.quotes_repository = quotes_repository
        self.checks_repository = checks_repository
        self.pre_opportunities_repository = pre_opportunities_repository
        self.auth_info = auth_info

    async def get_entity_data(
        self, entity_type: str, entity_id: UUID
    ) -> dict[str, Any]:

        entity_type_lower = entity_type.lower()

        if entity_type_lower == "order":
            return await self._get_order_data(entity_id)
        elif entity_type_lower == "invoice":
            return await self._get_invoice_data(entity_id)
        elif entity_type_lower == "quote":
            return await self._get_quote_data(entity_id)
        elif entity_type_lower == "check":
            return await self._get_check_data(entity_id)
        elif entity_type_lower in ["preopportunity", "pre_opportunity"]:
            return await self._get_pre_opportunity_data(entity_id)
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")

    async def _get_order_data(self, order_id: UUID) -> dict[str, Any]:

        from sqlalchemy.orm import selectinload
        from sqlalchemy import select

        stmt = select(Order).where(Order.id == order_id)

        try:
            if hasattr(Order, "line_items"):
                stmt = stmt.options(selectinload(Order.line_items))
            elif hasattr(Order, "order_line_items"):
                stmt = stmt.options(selectinload(Order.order_line_items))
        except AttributeError:

            pass

        result = await self.orders_repository.session.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundError(f"Order with id {order_id} not found")

        data: dict[str, Any] = {
            "id": str(order.id),
            "orderNumber": order.order_number,
            "entryDate": order.entry_date.isoformat() if order.entry_date else None,
            "entityDate": order.entity_date.isoformat() if order.entity_date else None,
            "shipDate": order.ship_date.isoformat() if order.ship_date else None,
            "dueDate": order.due_date.isoformat() if order.due_date else None,
            "status": order.status,
            "jobName": order.job_name,
            "factSoNumber": order.fact_so_number,
            "soldToCustomerId": str(order.sold_to_customer_id)
            if order.sold_to_customer_id
            else None,
            "billToCustomerId": str(order.bill_to_customer_id)
            if order.bill_to_customer_id
            else None,
            "quoteId": str(order.quote_id) if order.quote_id else None,
            "factoryId": str(order.factory_id) if order.factory_id else None,
            "balanceId": str(order.balance_id) if order.balance_id else None,
            "userOwnerIds": [str(uid) for uid in order.user_owner_ids]
            if order.user_owner_ids
            else [],
        }

        line_items: list[dict[str, Any]] = []
        line_items_attr = None
        if hasattr(order, "line_items"):
            line_items_attr = getattr(order, "line_items", None)
        elif hasattr(order, "order_line_items"):
            line_items_attr = getattr(order, "order_line_items", None)

        if line_items_attr:
            for line_item in line_items_attr:
                item_data: dict[str, Any] = {
                    "lineNumber": getattr(line_item, "line_number", getattr(line_item, "item_number", 0)),
                    "partNumber": getattr(line_item, "part_number", None),
                    "customerPartNumber": getattr(line_item, "customer_part_number", None),
                    "description": getattr(line_item, "description", None),
                    "quantityOrdered": float(getattr(line_item, "quantity", getattr(line_item, "quantity_ordered", 0))),
                    "quantityShipped": float(getattr(line_item, "quantity_shipped", 0)),
                    "quantityBackordered": float(getattr(line_item, "quantity_backordered", 0)),
                    "unitPrice": float(getattr(line_item, "unit_price", 0)) if getattr(line_item, "unit_price", None) else None,
                    "extendedPrice": float(getattr(line_item, "extended_price", 0)) if getattr(line_item, "extended_price", None) else None,
                    "discount": float(getattr(line_item, "discount", 0)) if getattr(line_item, "discount", None) else None,
                    "notes": getattr(line_item, "notes", None),
                    "consignmentFlag": bool(getattr(line_item, "is_consignment", getattr(line_item, "consignment_flag", False))),
                }
                line_items.append(item_data)

        data["lineItems"] = line_items

        return data

    async def _get_invoice_data(self, invoice_id: UUID) -> dict[str, Any]:

        from sqlalchemy.orm import selectinload
        from sqlalchemy import select

        stmt = select(Invoice).where(Invoice.id == invoice_id)

        try:
            if hasattr(Invoice, "line_items"):
                stmt = stmt.options(selectinload(Invoice.line_items))
            elif hasattr(Invoice, "invoice_line_items"):
                stmt = stmt.options(selectinload(Invoice.invoice_line_items))
        except AttributeError:
            pass

        result = await self.invoices_repository.session.execute(stmt)
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise NotFoundError(f"Invoice with id {invoice_id} not found")

        data: dict[str, Any] = {
            "id": str(invoice.id),
            "invoiceNumber": invoice.invoice_number,
            "entryDate": invoice.entry_date.isoformat()
            if invoice.entry_date
            else None,
            "entityDate": invoice.entity_date.isoformat()
            if invoice.entity_date
            else None,
            "dueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "status": invoice.status,
            "published": invoice.published,
            "locked": invoice.locked,
            "orderId": str(invoice.order_id) if invoice.order_id else None,
            "factoryId": str(invoice.factory_id) if invoice.factory_id else None,
            "balanceId": str(invoice.balance_id) if invoice.balance_id else None,
            "userOwnerIds": [str(uid) for uid in invoice.user_owner_ids]
            if invoice.user_owner_ids
            else [],
        }

        line_items: list[dict[str, Any]] = []
        line_items_attr = None
        if hasattr(invoice, "line_items"):
            line_items_attr = getattr(invoice, "line_items", None)
        elif hasattr(invoice, "invoice_line_items"):
            line_items_attr = getattr(invoice, "invoice_line_items", None)

        if line_items_attr:
            for line_item in line_items_attr:
                item_data: dict[str, Any] = {
                    "lineNumber": getattr(line_item, "line_number", getattr(line_item, "item_number", 0)),
                    "partNumber": getattr(line_item, "part_number", None),
                    "description": getattr(line_item, "description", None),
                    "quantity": float(getattr(line_item, "quantity", 0)),
                    "unitPrice": float(getattr(line_item, "unit_price", 0)) if getattr(line_item, "unit_price", None) else None,
                    "amount": float(getattr(line_item, "amount", getattr(line_item, "extended_price", 0))) if getattr(line_item, "amount", getattr(line_item, "extended_price", None)) else None,
                    "commissionRate": float(getattr(line_item, "commission_rate", 0)) if getattr(line_item, "commission_rate", None) else None,
                    "commissionAmount": float(getattr(line_item, "commission_amount", 0)) if getattr(line_item, "commission_amount", None) else None,
                }
                line_items.append(item_data)

        data["lineItems"] = line_items

        return data

    async def _get_quote_data(self, quote_id: UUID) -> dict[str, Any]:

        quote = await self.quotes_repository.get_by_id(quote_id)
        if not quote:
            raise NotFoundError(f"Quote with id {quote_id} not found")

        data: dict[str, Any] = {
            "id": str(quote.id),
            "quoteNumber": quote.quote_number,
            "entryDate": quote.entry_date.isoformat() if quote.entry_date else None,
            "entityDate": quote.entity_date.isoformat() if quote.entity_date else None,
            "expDate": quote.exp_date.isoformat() if quote.exp_date else None,
            "soldToCustomerId": str(quote.sold_to_customer_id)
            if quote.sold_to_customer_id
            else None,
            "billToCustomerId": str(quote.bill_to_customer_id)
            if quote.bill_to_customer_id
            else None,
            "jobName": quote.job_name,
            "blanket": quote.blanket,
            "userOwnerIds": [str(uid) for uid in quote.user_owner_ids]
            if quote.user_owner_ids
            else [],
        }

        data["lineItems"] = []

        return data

    async def _get_check_data(self, check_id: UUID) -> dict[str, Any]:

        check = await self.checks_repository.get_by_id(check_id)
        if not check:
            raise NotFoundError(f"Check with id {check_id} not found")

        data: dict[str, Any] = {
            "id": str(check.id),
            "checkNumber": getattr(check, "check_number", None),
            "checkDate": (
                getattr(check, "check_date", None).isoformat()
                if hasattr(check, "check_date") and getattr(check, "check_date", None)
                else None
            ),
            "amount": getattr(check, "amount", None),
            "status": getattr(check, "status", None),
        }

        return data

    async def _get_pre_opportunity_data(
        self, pre_opportunity_id: UUID
    ) -> dict[str, Any]:

        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from app.graphql.pre_opportunities.models.pre_opportunity_model import (
            PreOpportunity,
        )

        stmt = (
            select(PreOpportunity)
            .where(PreOpportunity.id == pre_opportunity_id)
            .options(selectinload(PreOpportunity.details))
        )
        result = await self.pre_opportunities_repository.session.execute(stmt)
        pre_opportunity = result.scalar_one_or_none()

        if not pre_opportunity:
            raise NotFoundError(
                f"PreOpportunity with id {pre_opportunity_id} not found"
            )

        status_value = (
            pre_opportunity.status.value
            if hasattr(pre_opportunity.status, "value")
            else int(pre_opportunity.status)
        )

        data: dict[str, Any] = {
            "id": str(pre_opportunity.id),
            "entityNumber": pre_opportunity.entity_number,
            "entityDate": pre_opportunity.entity_date.isoformat()
            if pre_opportunity.entity_date
            else None,
            "expDate": pre_opportunity.exp_date.isoformat()
            if pre_opportunity.exp_date
            else None,
            "reviseDate": pre_opportunity.revise_date.isoformat()
            if pre_opportunity.revise_date
            else None,
            "acceptDate": pre_opportunity.accept_date.isoformat()
            if pre_opportunity.accept_date
            else None,
            "status": status_value,
            "soldToCustomerId": str(pre_opportunity.sold_to_customer_id)
            if pre_opportunity.sold_to_customer_id
            else None,
            "billToCustomerId": str(pre_opportunity.bill_to_customer_id)
            if pre_opportunity.bill_to_customer_id
            else None,
            "jobId": str(pre_opportunity.job_id) if pre_opportunity.job_id else None,
            "paymentTerms": pre_opportunity.payment_terms,
            "freightTerms": pre_opportunity.freight_terms,
            "customerRef": pre_opportunity.customer_ref,
        }

        line_items: list[dict[str, Any]] = []
        if hasattr(pre_opportunity, "details") and pre_opportunity.details:
            for detail in pre_opportunity.details:
                product_name = None
                product_part_number = None
                if hasattr(detail, "product") and detail.product:
                    product_name = getattr(detail.product, "name", None)
                    product_part_number = getattr(
                        detail.product, "part_number", None
                    )

                line_item: dict[str, Any] = {
                    "lineNumber": detail.item_number,
                    "quantity": float(detail.quantity) if detail.quantity else 0,
                    "unitPrice": float(detail.unit_price) if detail.unit_price else 0,
                    "extendedPrice": float(detail.total) if detail.total else 0,
                    "discount": float(detail.discount) if detail.discount else 0,
                    "discountRate": float(detail.discount_rate)
                    if detail.discount_rate
                    else 0,
                    "subtotal": float(detail.subtotal) if detail.subtotal else 0,
                    "leadTime": detail.lead_time,
                    "partNumber": product_part_number,
                    "description": product_name,
                    "manufacturer": None,
                }
                line_items.append(line_item)

        data["lineItems"] = line_items

        return data

