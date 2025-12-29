import uuid
from uuid import UUID
from decimal import Decimal

from commons.db.v6.crm.shipment_requests.shipment_request import (
    ShipmentRequest,
    ShipmentRequestStatus,
    ShipmentPriority,
)
from commons.db.v6.crm.shipment_requests.shipment_request_item import (
    ShipmentRequestItem,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.v2.core.backorders.strawberry.backorder_response import (
    BackorderResponse,
)
from app.graphql.v2.core.backorders.repositories.backorder_repository import (
    BackorderRepository,
)
from app.graphql.v2.core.inventory.repositories.inventory_repository import (
    InventoryRepository,
)
from app.graphql.v2.core.shipment_requests.repositories.shipment_request_repository import (
    ShipmentRequestRepository,
)


class BackorderService:
    def __init__(
        self,
        repository: BackorderRepository,
        shipment_request_repository: ShipmentRequestRepository,
        inventory_repository: InventoryRepository,  # For context if needed
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        self.repository = repository
        self.shipment_request_repository = shipment_request_repository
        self.inventory_repository = inventory_repository
        self.context_wrapper = context_wrapper
        self.session = session

    async def get_backorders(
        self,
        warehouse_id: UUID | None = None,
        customer_id: UUID | None = None,
        product_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BackorderResponse]:
        return await self.repository.get_backorders(
            warehouse_id=warehouse_id,
            customer_id=customer_id,
            product_id=product_id,
            limit=limit,
            offset=offset,
        )

    async def restock(
        self,
        factory_id: UUID,
        items: list[tuple[UUID, Decimal]],  # product_id, quantity
        warehouse_id: UUID,
    ) -> ShipmentRequest:
        """
        Create a ShipmentRequest from Factory to Warehouse (Restock).
        """
        request = ShipmentRequest(
            request_number=str(uuid.uuid4()),  # Placeholder, should generate proper ID
            warehouse_id=warehouse_id,
            factory_id=factory_id,
            status=ShipmentRequestStatus.PENDING,
            priority=ShipmentPriority.STANDARD,
        )
        request.created_by_id = self.context_wrapper.get().auth_info.flow_user_id
        self.session.add(request)
        await self.session.flush()

        for product_id, quantity in items:
            item = ShipmentRequestItem(
                request_id=request.id,
                product_id=product_id,
                quantity=quantity,
            )
            item.created_by_id = self.context_wrapper.get().auth_info.flow_user_id
            self.session.add(item)
        
        await self.session.flush()
        return request

    async def dropship(
        self,
        factory_id: UUID,
        items: list[tuple[UUID, Decimal]],  # product_id, quantity
        customer_id: UUID,
    ) -> ShipmentRequest:
        """
        Create a ShipmentRequest from Factory to Customer (Dropship).
        """
        request = ShipmentRequest(
            request_number=str(uuid.uuid4()),  # Placeholder
            # warehouse_id is None for dropship strictly speaking, or could be passed if tracking is needed
            warehouse_id=None, 
            customer_id=customer_id,
            factory_id=factory_id,
            status=ShipmentRequestStatus.PENDING,
            priority=ShipmentPriority.STANDARD,
        )
        request.created_by_id = self.context_wrapper.get().auth_info.flow_user_id
        self.session.add(request)
        await self.session.flush()

        for product_id, quantity in items:
            item = ShipmentRequestItem(
                request_id=request.id,
                product_id=product_id,
                quantity=quantity,
            )
            item.created_by_id = self.context_wrapper.get().auth_info.flow_user_id
            self.session.add(item)
        
        await self.session.flush()
        return request
