# Fulfillment Backend Implementation Guide

> **Version:** 1.0
> **Target Backend:** flow-py-backend
> **Models Location:** flowbot-commons

---

## Table of Contents

1. [Overview](#1-overview)
2. [Database Models](#2-database-models)
3. [Enums](#3-enums)
4. [GraphQL Layer](#4-graphql-layer)
5. [Service Layer](#5-service-layer)
6. [Repository Layer](#6-repository-layer)
7. [Alembic Migrations](#7-alembic-migrations)
8. [Implementation Phases](#8-implementation-phases)
9. [Testing Strategy](#9-testing-strategy)

---

## 1. Overview

### 1.1 Purpose

This document provides the implementation specification for the Warehouse Fulfillment System backend. The frontend UI is complete with mock data; this backend will replace those mocks with real data persistence and business logic.

### 1.2 Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    GraphQL API Layer                         │
│   Queries & Mutations (Strawberry)                          │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer                             │
│   Business Logic, Orchestration, Validation                  │
├─────────────────────────────────────────────────────────────┤
│                    Repository Layer                          │
│   Data Access, SQLAlchemy Queries                           │
├─────────────────────────────────────────────────────────────┤
│                    Database Models                           │
│   SQLAlchemy ORM (flowbot-commons)                          │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Directory Structure

```
flow-py-backend/
└── app/graphql/v2/core/fulfillment/
    ├── __init__.py
    ├── queries.py
    ├── mutations.py
    ├── repositories/
    │   ├── __init__.py
    │   ├── fulfillment_order_repository.py
    │   ├── fulfillment_line_repository.py
    │   ├── packing_box_repository.py
    │   └── fulfillment_activity_repository.py
    ├── services/
    │   ├── __init__.py
    │   ├── fulfillment_order_service.py
    │   ├── fulfillment_picking_service.py
    │   ├── fulfillment_packing_service.py
    │   ├── fulfillment_shipping_service.py
    │   └── fulfillment_backorder_service.py
    ├── strawberry/
    │   ├── __init__.py
    │   ├── fulfillment_order_input.py
    │   ├── fulfillment_order_response.py
    │   ├── fulfillment_line_input.py
    │   ├── fulfillment_line_response.py
    │   ├── packing_box_input.py
    │   ├── packing_box_response.py
    │   ├── fulfillment_activity_response.py
    │   └── enums.py
    └── factories/
        ├── __init__.py
        └── fulfillment_order_factory.py

flowbot-commons/
└── commons/db/v6/fulfillment/
    ├── __init__.py
    ├── fulfillment_order.py
    ├── fulfillment_order_line_item.py
    ├── fulfillment_assignment.py
    ├── fulfillment_activity.py
    ├── packing_box.py
    ├── packing_box_item.py
    └── enums.py
```

---

## 2. Database Models

All models use the `pywarehouse` schema and extend `PyWarehouseBaseModel`.

### 2.1 FulfillmentOrder

**File:** `commons/db/v6/fulfillment/fulfillment_order.py`

```python
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db.v6.fulfillment.enums import (
    CarrierType,
    FulfillmentMethod,
    FulfillmentOrderStatus,
)
from commons.db.v6.warehouse.base import PyWarehouseBaseModel
from commons.db.v6.warehouse.mixins import HasCreatedAt, HasCreatedBy, HasUpdatedAt

if TYPE_CHECKING:
    from commons.db.v6.fulfillment.fulfillment_activity import FulfillmentActivity
    from commons.db.v6.fulfillment.fulfillment_assignment import FulfillmentAssignment
    from commons.db.v6.fulfillment.fulfillment_order_line_item import (
        FulfillmentOrderLineItem,
    )
    from commons.db.v6.fulfillment.packing_box import PackingBox
    from commons.db.v6.warehouse.shipping_carrier import ShippingCarrier
    from commons.db.v6.warehouse.warehouse import Warehouse


class FulfillmentOrder(PyWarehouseBaseModel, HasCreatedAt, HasCreatedBy, HasUpdatedAt):
    __tablename__ = "fulfillment_orders"

    # Identifiers
    fulfillment_order_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    # Foreign Keys
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pycommission.orders.id"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.warehouses.id"),
        nullable=False,
        index=True,
    )
    carrier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.shipping_carriers.id"),
        nullable=True,
    )

    # Status
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=FulfillmentOrderStatus.PENDING,
        index=True,
    )

    # Fulfillment Configuration
    fulfillment_method: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=FulfillmentMethod.SHIP,
    )
    carrier_type: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Ship-to Address (JSON)
    ship_to_customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pycrm.customers.id"),
        nullable=True,
    )
    ship_to_address: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Dates
    need_by_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Timestamps
    released_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pick_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pick_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pack_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ship_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Shipping Details
    tracking_numbers: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )
    bol_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pro_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Signature Capture
    pickup_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    pickup_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    pickup_customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    driver_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Backorder
    has_backorder_items: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    hold_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    backorder_review_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse",
        lazy="joined",
    )
    carrier: Mapped["ShippingCarrier | None"] = relationship(
        "ShippingCarrier",
        lazy="joined",
    )
    line_items: Mapped[list["FulfillmentOrderLineItem"]] = relationship(
        "FulfillmentOrderLineItem",
        back_populates="fulfillment_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    packing_boxes: Mapped[list["PackingBox"]] = relationship(
        "PackingBox",
        back_populates="fulfillment_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    assignments: Mapped[list["FulfillmentAssignment"]] = relationship(
        "FulfillmentAssignment",
        back_populates="fulfillment_order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["FulfillmentActivity"]] = relationship(
        "FulfillmentActivity",
        back_populates="fulfillment_order",
        lazy="selectin",
        order_by="FulfillmentActivity.created_at.desc()",
        cascade="all, delete-orphan",
    )

    @property
    def status_enum(self) -> FulfillmentOrderStatus:
        return FulfillmentOrderStatus(self.status)

    @property
    def fulfillment_method_enum(self) -> FulfillmentMethod:
        return FulfillmentMethod(self.fulfillment_method)

    @property
    def carrier_type_enum(self) -> CarrierType | None:
        return CarrierType(self.carrier_type) if self.carrier_type else None
```

### 2.2 FulfillmentOrderLineItem

**File:** `commons/db/v6/fulfillment/fulfillment_order_line_item.py`

```python
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db.v6.warehouse.base import PyWarehouseBaseModel

if TYPE_CHECKING:
    from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder
    from commons.db.v6.fulfillment.packing_box_item import PackingBoxItem
    from commons.db.v6.warehouse.warehouse_location import WarehouseLocation


class FulfillmentOrderLineItem(PyWarehouseBaseModel):
    __tablename__ = "fulfillment_order_line_items"

    # Foreign Keys
    fulfillment_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.fulfillment_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_detail_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pycommission.order_details.id"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pycrm.products.id"),
        nullable=False,
        index=True,
    )

    # Quantities (using Decimal for precision)
    ordered_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )
    allocated_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )
    picked_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )
    packed_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )
    shipped_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )
    backorder_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )

    # Manufacturer Fulfillment
    fulfilled_by_manufacturer: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    manufacturer_fulfillment_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    linked_shipment_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Picking Details
    pick_location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.warehouse_locations.id"),
        nullable=True,
    )
    short_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    fulfillment_order: Mapped["FulfillmentOrder"] = relationship(
        "FulfillmentOrder",
        back_populates="line_items",
    )
    pick_location: Mapped["WarehouseLocation | None"] = relationship(
        "WarehouseLocation",
        lazy="joined",
    )
    packing_box_items: Mapped[list["PackingBoxItem"]] = relationship(
        "PackingBoxItem",
        back_populates="fulfillment_line_item",
        lazy="selectin",
    )
```

### 2.3 FulfillmentAssignment

**File:** `commons/db/v6/fulfillment/fulfillment_assignment.py`

```python
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db.v6.fulfillment.enums import FulfillmentAssignmentRole
from commons.db.v6.warehouse.base import PyWarehouseBaseModel
from commons.db.v6.warehouse.mixins import HasCreatedAt, HasCreatedBy

if TYPE_CHECKING:
    from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder


class FulfillmentAssignment(PyWarehouseBaseModel, HasCreatedAt, HasCreatedBy):
    __tablename__ = "fulfillment_assignments"

    fulfillment_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.fulfillment_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pycrm.users.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Relationships
    fulfillment_order: Mapped["FulfillmentOrder"] = relationship(
        "FulfillmentOrder",
        back_populates="assignments",
    )

    @property
    def role_enum(self) -> FulfillmentAssignmentRole:
        return FulfillmentAssignmentRole(self.role)
```

### 2.4 FulfillmentActivity

**File:** `commons/db/v6/fulfillment/fulfillment_activity.py`

```python
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db.v6.fulfillment.enums import FulfillmentActivityType
from commons.db.v6.warehouse.base import PyWarehouseBaseModel
from commons.db.v6.warehouse.mixins import HasCreatedAt, HasCreatedBy

if TYPE_CHECKING:
    from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder


class FulfillmentActivity(PyWarehouseBaseModel, HasCreatedAt, HasCreatedBy):
    __tablename__ = "fulfillment_activities"

    fulfillment_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.fulfillment_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_type: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    fulfillment_order: Mapped["FulfillmentOrder"] = relationship(
        "FulfillmentOrder",
        back_populates="activities",
    )

    @property
    def activity_type_enum(self) -> FulfillmentActivityType:
        return FulfillmentActivityType(self.activity_type)
```

### 2.5 PackingBox

**File:** `commons/db/v6/fulfillment/packing_box.py`

```python
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db.v6.warehouse.base import PyWarehouseBaseModel
from commons.db.v6.warehouse.mixins import HasCreatedAt

if TYPE_CHECKING:
    from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder
    from commons.db.v6.fulfillment.packing_box_item import PackingBoxItem
    from commons.db.v6.warehouse.container_type import ContainerType


class PackingBox(PyWarehouseBaseModel, HasCreatedAt):
    __tablename__ = "packing_boxes"

    fulfillment_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.fulfillment_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    container_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.container_types.id"),
        nullable=True,
    )
    box_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Dimensions
    length: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    width: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    height: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Tracking
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    label_printed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    fulfillment_order: Mapped["FulfillmentOrder"] = relationship(
        "FulfillmentOrder",
        back_populates="packing_boxes",
    )
    container_type: Mapped["ContainerType | None"] = relationship(
        "ContainerType",
        lazy="joined",
    )
    items: Mapped[list["PackingBoxItem"]] = relationship(
        "PackingBoxItem",
        back_populates="packing_box",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
```

### 2.6 PackingBoxItem

**File:** `commons/db/v6/fulfillment/packing_box_item.py`

```python
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db.v6.warehouse.base import PyWarehouseBaseModel

if TYPE_CHECKING:
    from commons.db.v6.fulfillment.fulfillment_order_line_item import (
        FulfillmentOrderLineItem,
    )
    from commons.db.v6.fulfillment.packing_box import PackingBox


class PackingBoxItem(PyWarehouseBaseModel):
    __tablename__ = "packing_box_items"

    packing_box_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.packing_boxes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fulfillment_line_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pywarehouse.fulfillment_order_line_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    # Relationships
    packing_box: Mapped["PackingBox"] = relationship(
        "PackingBox",
        back_populates="items",
    )
    fulfillment_line_item: Mapped["FulfillmentOrderLineItem"] = relationship(
        "FulfillmentOrderLineItem",
        back_populates="packing_box_items",
    )
```

---

## 3. Enums

**File:** `commons/db/v6/fulfillment/enums.py`

```python
from enum import IntEnum, auto


class FulfillmentOrderStatus(IntEnum):
    PENDING = auto()
    RELEASED = auto()
    PICKING = auto()
    PACKING = auto()
    SHIPPING = auto()
    SHIPPED = auto()
    COMMUNICATED = auto()
    DELIVERED = auto()
    BACKORDER_REVIEW = auto()
    PARTIAL_SHIPPED = auto()
    CANCELLED = auto()


class FulfillmentMethod(IntEnum):
    SHIP = auto()
    WILL_CALL = auto()


class CarrierType(IntEnum):
    PARCEL = auto()
    FREIGHT = auto()


class FulfillmentAssignmentRole(IntEnum):
    MANAGER = auto()
    WORKER = auto()
    INSIDE_SALES = auto()


class FulfillmentActivityType(IntEnum):
    CREATED = auto()
    RELEASED = auto()
    PICK_STARTED = auto()
    PICK_COMPLETED = auto()
    PACK_STARTED = auto()
    PACK_COMPLETED = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()
    NOTE_ADDED = auto()
    ITEM_NOTE_ADDED = auto()
    BACKORDER_REPORTED = auto()
    ASSIGNMENT_ADDED = auto()
    ASSIGNMENT_REMOVED = auto()
    SIGNATURE_CAPTURED = auto()
    TRACKING_ADDED = auto()
```

---

## 4. GraphQL Layer

### 4.1 Strawberry Response Types

**File:** `app/graphql/v2/core/fulfillment/strawberry/fulfillment_order_response.py`

```python
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Self

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.fulfillment.strawberry.enums import (
    CarrierTypeGQL,
    FulfillmentMethodGQL,
    FulfillmentOrderStatusGQL,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_activity_response import (
    FulfillmentActivityResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_response import (
    FulfillmentOrderLineItemResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.packing_box_response import (
    PackingBoxResponse,
)
from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder


@strawberry.type
class ShipToAddressResponse:
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


@strawberry.type
class AssignedUserResponse:
    id: uuid.UUID
    name: str
    email: str
    role: str


@strawberry.type
class FulfillmentOrderResponse(DTOMixin[FulfillmentOrder]):
    _instance: strawberry.Private[FulfillmentOrder]

    id: uuid.UUID
    fulfillment_order_number: str
    order_id: uuid.UUID
    warehouse_id: uuid.UUID
    status: FulfillmentOrderStatusGQL
    fulfillment_method: FulfillmentMethodGQL
    carrier_type: CarrierTypeGQL | None
    need_by_date: date | None
    has_backorder_items: bool

    # Timestamps
    released_at: datetime | None
    pick_started_at: datetime | None
    pick_completed_at: datetime | None
    pack_completed_at: datetime | None
    ship_confirmed_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime

    # Shipping
    tracking_numbers: list[str]
    bol_number: str | None
    pro_number: str | None

    # Signature
    pickup_signature: str | None
    pickup_timestamp: datetime | None
    pickup_customer_name: str | None
    driver_name: str | None

    @classmethod
    def from_orm_model(cls, model: FulfillmentOrder) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            fulfillment_order_number=model.fulfillment_order_number,
            order_id=model.order_id,
            warehouse_id=model.warehouse_id,
            status=FulfillmentOrderStatusGQL(model.status),
            fulfillment_method=FulfillmentMethodGQL(model.fulfillment_method),
            carrier_type=(
                CarrierTypeGQL(model.carrier_type) if model.carrier_type else None
            ),
            need_by_date=model.need_by_date,
            has_backorder_items=model.has_backorder_items,
            released_at=model.released_at,
            pick_started_at=model.pick_started_at,
            pick_completed_at=model.pick_completed_at,
            pack_completed_at=model.pack_completed_at,
            ship_confirmed_at=model.ship_confirmed_at,
            delivered_at=model.delivered_at,
            created_at=model.created_at,
            tracking_numbers=model.tracking_numbers or [],
            bol_number=model.bol_number,
            pro_number=model.pro_number,
            pickup_signature=model.pickup_signature,
            pickup_timestamp=model.pickup_timestamp,
            pickup_customer_name=model.pickup_customer_name,
            driver_name=model.driver_name,
        )

    @strawberry.field
    async def warehouse_name(self) -> str:
        warehouse = await self._instance.awaitable_attrs.warehouse
        return warehouse.name if warehouse else ""

    @strawberry.field
    async def carrier_name(self) -> str | None:
        carrier = await self._instance.awaitable_attrs.carrier
        return carrier.name if carrier else None

    @strawberry.field
    async def ship_to_address(self) -> ShipToAddressResponse | None:
        addr = self._instance.ship_to_address
        if not addr:
            return None
        return ShipToAddressResponse(
            street=addr.get("street"),
            city=addr.get("city"),
            state=addr.get("state"),
            postal_code=addr.get("postal_code"),
            country=addr.get("country"),
        )

    @strawberry.field
    async def line_items(self) -> list[FulfillmentOrderLineItemResponse]:
        items = await self._instance.awaitable_attrs.line_items
        return FulfillmentOrderLineItemResponse.from_orm_model_list(items)

    @strawberry.field
    async def packing_boxes(self) -> list[PackingBoxResponse]:
        boxes = await self._instance.awaitable_attrs.packing_boxes
        return PackingBoxResponse.from_orm_model_list(boxes)

    @strawberry.field
    async def activities(self) -> list[FulfillmentActivityResponse]:
        activities = await self._instance.awaitable_attrs.activities
        return FulfillmentActivityResponse.from_orm_model_list(activities)

    @strawberry.field
    async def assigned_managers(self) -> list[AssignedUserResponse]:
        from commons.db.v6.fulfillment.enums import FulfillmentAssignmentRole

        assignments = await self._instance.awaitable_attrs.assignments
        return [
            AssignedUserResponse(
                id=a.user_id,
                name="",  # Resolved via user service
                email="",
                role="MANAGER",
            )
            for a in assignments
            if a.role == FulfillmentAssignmentRole.MANAGER
        ]

    @strawberry.field
    async def assigned_workers(self) -> list[AssignedUserResponse]:
        from commons.db.v6.fulfillment.enums import FulfillmentAssignmentRole

        assignments = await self._instance.awaitable_attrs.assignments
        return [
            AssignedUserResponse(
                id=a.user_id,
                name="",
                email="",
                role="WORKER",
            )
            for a in assignments
            if a.role == FulfillmentAssignmentRole.WORKER
        ]
```

### 4.2 Strawberry Input Types

**File:** `app/graphql/v2/core/fulfillment/strawberry/fulfillment_order_input.py`

```python
import uuid
from datetime import date
from decimal import Decimal

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.fulfillment.strawberry.enums import (
    CarrierTypeGQL,
    FulfillmentMethodGQL,
)
from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder


@strawberry.input
class ShipToAddressInput:
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


@strawberry.input
class CreateFulfillmentOrderInput(BaseInputGQL[FulfillmentOrder]):
    order_id: uuid.UUID
    warehouse_id: uuid.UUID
    fulfillment_method: FulfillmentMethodGQL = FulfillmentMethodGQL.SHIP
    carrier_id: uuid.UUID | None = None
    carrier_type: CarrierTypeGQL | None = None
    ship_to_address: ShipToAddressInput | None = None
    need_by_date: date | None = None

    def to_orm_model(self) -> FulfillmentOrder:
        return FulfillmentOrder(
            order_id=self.order_id,
            warehouse_id=self.warehouse_id,
            fulfillment_method=self.fulfillment_method.value,
            carrier_id=self.carrier_id,
            carrier_type=self.carrier_type.value if self.carrier_type else None,
            ship_to_address=(
                {
                    "street": self.ship_to_address.street,
                    "city": self.ship_to_address.city,
                    "state": self.ship_to_address.state,
                    "postal_code": self.ship_to_address.postal_code,
                    "country": self.ship_to_address.country,
                }
                if self.ship_to_address
                else None
            ),
            need_by_date=self.need_by_date,
        )


@strawberry.input
class UpdateFulfillmentOrderInput:
    warehouse_id: uuid.UUID | None = strawberry.UNSET
    carrier_id: uuid.UUID | None = strawberry.UNSET
    carrier_type: CarrierTypeGQL | None = strawberry.UNSET
    ship_to_address: ShipToAddressInput | None = strawberry.UNSET
    need_by_date: date | None = strawberry.UNSET
    hold_reason: str | None = strawberry.UNSET


@strawberry.input
class UpdatePickedQuantityInput:
    line_item_id: uuid.UUID
    quantity: Decimal
    location_id: uuid.UUID | None = None
    notes: str | None = None


@strawberry.input
class AssignItemToBoxInput:
    box_id: uuid.UUID
    line_item_id: uuid.UUID
    quantity: Decimal


@strawberry.input
class CompleteShippingInput:
    tracking_numbers: list[str] | None = None
    bol_number: str | None = None
    pro_number: str | None = None
    signature: str | None = None
    driver_name: str | None = None
    pickup_customer_name: str | None = None


@strawberry.input
class BulkAssignmentInput:
    fulfillment_order_ids: list[uuid.UUID]
    manager_ids: list[uuid.UUID] | None = None
    worker_ids: list[uuid.UUID] | None = None
```

### 4.3 GraphQL Enums

**File:** `app/graphql/v2/core/fulfillment/strawberry/enums.py`

```python
import strawberry

from commons.db.v6.fulfillment.enums import (
    CarrierType,
    FulfillmentActivityType,
    FulfillmentAssignmentRole,
    FulfillmentMethod,
    FulfillmentOrderStatus,
)


@strawberry.enum
class FulfillmentOrderStatusGQL(strawberry.enum.Enum):
    PENDING = FulfillmentOrderStatus.PENDING
    RELEASED = FulfillmentOrderStatus.RELEASED
    PICKING = FulfillmentOrderStatus.PICKING
    PACKING = FulfillmentOrderStatus.PACKING
    SHIPPING = FulfillmentOrderStatus.SHIPPING
    SHIPPED = FulfillmentOrderStatus.SHIPPED
    COMMUNICATED = FulfillmentOrderStatus.COMMUNICATED
    DELIVERED = FulfillmentOrderStatus.DELIVERED
    BACKORDER_REVIEW = FulfillmentOrderStatus.BACKORDER_REVIEW
    PARTIAL_SHIPPED = FulfillmentOrderStatus.PARTIAL_SHIPPED
    CANCELLED = FulfillmentOrderStatus.CANCELLED


@strawberry.enum
class FulfillmentMethodGQL(strawberry.enum.Enum):
    SHIP = FulfillmentMethod.SHIP
    WILL_CALL = FulfillmentMethod.WILL_CALL


@strawberry.enum
class CarrierTypeGQL(strawberry.enum.Enum):
    PARCEL = CarrierType.PARCEL
    FREIGHT = CarrierType.FREIGHT


@strawberry.enum
class FulfillmentAssignmentRoleGQL(strawberry.enum.Enum):
    MANAGER = FulfillmentAssignmentRole.MANAGER
    WORKER = FulfillmentAssignmentRole.WORKER
    INSIDE_SALES = FulfillmentAssignmentRole.INSIDE_SALES


@strawberry.enum
class FulfillmentActivityTypeGQL(strawberry.enum.Enum):
    CREATED = FulfillmentActivityType.CREATED
    RELEASED = FulfillmentActivityType.RELEASED
    PICK_STARTED = FulfillmentActivityType.PICK_STARTED
    PICK_COMPLETED = FulfillmentActivityType.PICK_COMPLETED
    PACK_STARTED = FulfillmentActivityType.PACK_STARTED
    PACK_COMPLETED = FulfillmentActivityType.PACK_COMPLETED
    SHIPPED = FulfillmentActivityType.SHIPPED
    DELIVERED = FulfillmentActivityType.DELIVERED
    CANCELLED = FulfillmentActivityType.CANCELLED
    NOTE_ADDED = FulfillmentActivityType.NOTE_ADDED
    ITEM_NOTE_ADDED = FulfillmentActivityType.ITEM_NOTE_ADDED
    BACKORDER_REPORTED = FulfillmentActivityType.BACKORDER_REPORTED
    ASSIGNMENT_ADDED = FulfillmentActivityType.ASSIGNMENT_ADDED
    ASSIGNMENT_REMOVED = FulfillmentActivityType.ASSIGNMENT_REMOVED
    SIGNATURE_CAPTURED = FulfillmentActivityType.SIGNATURE_CAPTURED
    TRACKING_ADDED = FulfillmentActivityType.TRACKING_ADDED
```

### 4.4 Queries

**File:** `app/graphql/v2/core/fulfillment/queries.py`

```python
import uuid

import strawberry

from app.graphql.inject import Injected, inject
from app.graphql.v2.core.fulfillment.services.fulfillment_order_service import (
    FulfillmentOrderService,
)
from app.graphql.v2.core.fulfillment.strawberry.enums import FulfillmentOrderStatusGQL
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_response import (
    FulfillmentOrderResponse,
)


@strawberry.type
class FulfillmentStatsResponse:
    pending_count: int
    in_progress_count: int
    completed_count: int
    backorder_count: int


@strawberry.type
class FulfillmentQueries:
    @strawberry.field
    @inject
    async def fulfillment_orders(
        self,
        service: Injected[FulfillmentOrderService],
        warehouse_id: uuid.UUID | None = None,
        status: list[FulfillmentOrderStatusGQL] | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FulfillmentOrderResponse]:
        status_values = [s.value for s in status] if status else None
        orders = await service.list_orders(
            warehouse_id=warehouse_id,
            status=status_values,
            search=search,
            limit=limit,
            offset=offset,
        )
        return FulfillmentOrderResponse.from_orm_model_list(orders)

    @strawberry.field
    @inject
    async def fulfillment_order(
        self,
        id: uuid.UUID,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse | None:
        order = await service.get_by_id(id)
        return FulfillmentOrderResponse.from_orm_model(order) if order else None

    @strawberry.field
    @inject
    async def fulfillment_stats(
        self,
        service: Injected[FulfillmentOrderService],
        warehouse_id: uuid.UUID | None = None,
    ) -> FulfillmentStatsResponse:
        stats = await service.get_stats(warehouse_id)
        return FulfillmentStatsResponse(
            pending_count=stats["pending"],
            in_progress_count=stats["in_progress"],
            completed_count=stats["completed"],
            backorder_count=stats["backorder"],
        )
```

### 4.5 Mutations

**File:** `app/graphql/v2/core/fulfillment/mutations.py`

```python
import uuid
from decimal import Decimal

import strawberry

from app.graphql.inject import Injected, inject
from app.graphql.v2.core.fulfillment.services.fulfillment_backorder_service import (
    FulfillmentBackorderService,
)
from app.graphql.v2.core.fulfillment.services.fulfillment_order_service import (
    FulfillmentOrderService,
)
from app.graphql.v2.core.fulfillment.services.fulfillment_packing_service import (
    FulfillmentPackingService,
)
from app.graphql.v2.core.fulfillment.services.fulfillment_picking_service import (
    FulfillmentPickingService,
)
from app.graphql.v2.core.fulfillment.services.fulfillment_shipping_service import (
    FulfillmentShippingService,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_response import (
    FulfillmentOrderLineItemResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_input import (
    AssignItemToBoxInput,
    BulkAssignmentInput,
    CompleteShippingInput,
    CreateFulfillmentOrderInput,
    UpdateFulfillmentOrderInput,
    UpdatePickedQuantityInput,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_response import (
    FulfillmentOrderResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.packing_box_response import (
    PackingBoxResponse,
)


@strawberry.type
class FulfillmentMutations:
    # ─────────────────────────────────────────────────────────────────
    # Order Lifecycle
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def create_fulfillment_order(
        self,
        input: CreateFulfillmentOrderInput,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.create(input)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def update_fulfillment_order(
        self,
        id: uuid.UUID,
        input: UpdateFulfillmentOrderInput,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.update(id, input)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def release_to_warehouse(
        self,
        id: uuid.UUID,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.release_to_warehouse(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def cancel_fulfillment_order(
        self,
        id: uuid.UUID,
        reason: str,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.cancel(id, reason)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Assignments
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def bulk_assign_fulfillment_orders(
        self,
        input: BulkAssignmentInput,
        service: Injected[FulfillmentOrderService],
    ) -> list[FulfillmentOrderResponse]:
        orders = await service.bulk_assign(input)
        return FulfillmentOrderResponse.from_orm_model_list(orders)

    # ─────────────────────────────────────────────────────────────────
    # Picking
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def start_picking(
        self,
        id: uuid.UUID,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderResponse:
        order = await service.start_picking(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def update_picked_quantity(
        self,
        input: UpdatePickedQuantityInput,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderLineItemResponse:
        line_item = await service.update_picked_quantity(
            line_item_id=input.line_item_id,
            quantity=input.quantity,
            location_id=input.location_id,
            notes=input.notes,
        )
        return FulfillmentOrderLineItemResponse.from_orm_model(line_item)

    @strawberry.mutation
    @inject
    async def complete_picking(
        self,
        id: uuid.UUID,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderResponse:
        order = await service.complete_picking(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def report_inventory_discrepancy(
        self,
        line_item_id: uuid.UUID,
        actual_quantity: Decimal,
        reason: str,
        service: Injected[FulfillmentPickingService],
    ) -> FulfillmentOrderResponse:
        order = await service.report_discrepancy(line_item_id, actual_quantity, reason)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Packing
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def add_packing_box(
        self,
        fulfillment_order_id: uuid.UUID,
        container_type_id: uuid.UUID | None,
        service: Injected[FulfillmentPackingService],
    ) -> PackingBoxResponse:
        box = await service.add_box(fulfillment_order_id, container_type_id)
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def update_packing_box(
        self,
        box_id: uuid.UUID,
        length: Decimal | None = None,
        width: Decimal | None = None,
        height: Decimal | None = None,
        weight: Decimal | None = None,
        service: Injected[FulfillmentPackingService] = None,
    ) -> PackingBoxResponse:
        box = await service.update_box(box_id, length, width, height, weight)
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def assign_item_to_box(
        self,
        input: AssignItemToBoxInput,
        service: Injected[FulfillmentPackingService],
    ) -> PackingBoxResponse:
        box = await service.assign_item(
            box_id=input.box_id,
            line_item_id=input.line_item_id,
            quantity=input.quantity,
        )
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def remove_item_from_box(
        self,
        box_id: uuid.UUID,
        line_item_id: uuid.UUID,
        service: Injected[FulfillmentPackingService],
    ) -> PackingBoxResponse:
        box = await service.remove_item(box_id, line_item_id)
        return PackingBoxResponse.from_orm_model(box)

    @strawberry.mutation
    @inject
    async def delete_packing_box(
        self,
        box_id: uuid.UUID,
        service: Injected[FulfillmentPackingService],
    ) -> bool:
        return await service.delete_box(box_id)

    @strawberry.mutation
    @inject
    async def complete_packing(
        self,
        id: uuid.UUID,
        service: Injected[FulfillmentPackingService],
    ) -> FulfillmentOrderResponse:
        order = await service.complete_packing(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Shipping
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def complete_shipping(
        self,
        id: uuid.UUID,
        input: CompleteShippingInput,
        service: Injected[FulfillmentShippingService],
    ) -> FulfillmentOrderResponse:
        order = await service.complete_shipping(id, input)
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def mark_delivered(
        self,
        id: uuid.UUID,
        service: Injected[FulfillmentShippingService],
    ) -> FulfillmentOrderResponse:
        order = await service.mark_delivered(id)
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Backorder
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def mark_manufacturer_direct(
        self,
        fulfillment_order_id: uuid.UUID,
        line_item_ids: list[uuid.UUID],
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderResponse:
        order = await service.mark_manufacturer_direct(
            fulfillment_order_id, line_item_ids
        )
        return FulfillmentOrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def split_fulfillment_line_item(
        self,
        line_item_id: uuid.UUID,
        warehouse_qty: Decimal,
        manufacturer_qty: Decimal,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderLineItemResponse:
        line_item = await service.split_line_item(
            line_item_id, warehouse_qty, manufacturer_qty
        )
        return FulfillmentOrderLineItemResponse.from_orm_model(line_item)

    @strawberry.mutation
    @inject
    async def cancel_backorder_items(
        self,
        fulfillment_order_id: uuid.UUID,
        line_item_ids: list[uuid.UUID],
        reason: str,
        service: Injected[FulfillmentBackorderService],
    ) -> FulfillmentOrderResponse:
        order = await service.cancel_backorder_items(
            fulfillment_order_id, line_item_ids, reason
        )
        return FulfillmentOrderResponse.from_orm_model(order)

    # ─────────────────────────────────────────────────────────────────
    # Activity / Notes
    # ─────────────────────────────────────────────────────────────────

    @strawberry.mutation
    @inject
    async def add_fulfillment_note(
        self,
        fulfillment_order_id: uuid.UUID,
        content: str,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse:
        order = await service.add_note(fulfillment_order_id, content)
        return FulfillmentOrderResponse.from_orm_model(order)
```

---

## 5. Service Layer

### 5.1 FulfillmentOrderService

**File:** `app/graphql/v2/core/fulfillment/services/fulfillment_order_service.py`

```python
import uuid
from datetime import datetime

from app.core.auth.auth_info import AuthInfo
from app.errors import NotFoundError
from app.graphql.v2.core.fulfillment.repositories.fulfillment_activity_repository import (
    FulfillmentActivityRepository,
)
from app.graphql.v2.core.fulfillment.repositories.fulfillment_order_repository import (
    FulfillmentOrderRepository,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_input import (
    BulkAssignmentInput,
    CreateFulfillmentOrderInput,
    UpdateFulfillmentOrderInput,
)
from commons.db.v6.fulfillment.enums import (
    FulfillmentActivityType,
    FulfillmentAssignmentRole,
    FulfillmentOrderStatus,
)
from commons.db.v6.fulfillment.fulfillment_activity import FulfillmentActivity
from commons.db.v6.fulfillment.fulfillment_assignment import FulfillmentAssignment
from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder


class FulfillmentOrderService:
    def __init__(
        self,
        repository: FulfillmentOrderRepository,
        activity_repository: FulfillmentActivityRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.activity_repository = activity_repository
        self.auth_info = auth_info

    async def get_by_id(self, order_id: uuid.UUID) -> FulfillmentOrder | None:
        return await self.repository.get_by_id(order_id)

    async def list_orders(
        self,
        warehouse_id: uuid.UUID | None = None,
        status: list[int] | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FulfillmentOrder]:
        return await self.repository.list_orders(
            warehouse_id=warehouse_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def get_stats(self, warehouse_id: uuid.UUID | None = None) -> dict[str, int]:
        return await self.repository.get_stats(warehouse_id)

    async def create(self, input: CreateFulfillmentOrderInput) -> FulfillmentOrder:
        order = input.to_orm_model()
        order.fulfillment_order_number = await self._generate_order_number()
        order.created_by_id = self.auth_info.user_id

        order = await self.repository.create(order)

        await self._log_activity(
            order.id,
            FulfillmentActivityType.CREATED,
            "Fulfillment order created",
        )

        return order

    async def update(
        self,
        order_id: uuid.UUID,
        input: UpdateFulfillmentOrderInput,
    ) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)

        if input.warehouse_id is not None:
            order.warehouse_id = input.warehouse_id
        if input.carrier_id is not None:
            order.carrier_id = input.carrier_id
        if input.carrier_type is not None:
            order.carrier_type = input.carrier_type.value if input.carrier_type else None
        if input.need_by_date is not None:
            order.need_by_date = input.need_by_date
        if input.hold_reason is not None:
            order.hold_reason = input.hold_reason

        return await self.repository.update(order)

    async def release_to_warehouse(self, order_id: uuid.UUID) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.PENDING:
            raise ValueError("Order must be in PENDING status to release")

        order.status = FulfillmentOrderStatus.RELEASED
        order.released_at = datetime.utcnow()

        # Auto-assign current user as manager
        assignment = FulfillmentAssignment(
            fulfillment_order_id=order.id,
            user_id=self.auth_info.user_id,
            role=FulfillmentAssignmentRole.MANAGER,
            created_by_id=self.auth_info.user_id,
        )
        order.assignments.append(assignment)

        order = await self.repository.update(order)

        await self._log_activity(
            order.id,
            FulfillmentActivityType.RELEASED,
            "Order released to warehouse",
        )

        return order

    async def cancel(self, order_id: uuid.UUID, reason: str) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)
        order.status = FulfillmentOrderStatus.CANCELLED
        order.hold_reason = reason

        order = await self.repository.update(order)

        await self._log_activity(
            order.id,
            FulfillmentActivityType.CANCELLED,
            f"Order cancelled: {reason}",
        )

        return order

    async def bulk_assign(
        self,
        input: BulkAssignmentInput,
    ) -> list[FulfillmentOrder]:
        orders = []
        for order_id in input.fulfillment_order_ids:
            order = await self._get_or_raise(order_id)

            if input.manager_ids:
                for user_id in input.manager_ids:
                    assignment = FulfillmentAssignment(
                        fulfillment_order_id=order.id,
                        user_id=user_id,
                        role=FulfillmentAssignmentRole.MANAGER,
                        created_by_id=self.auth_info.user_id,
                    )
                    order.assignments.append(assignment)

            if input.worker_ids:
                for user_id in input.worker_ids:
                    assignment = FulfillmentAssignment(
                        fulfillment_order_id=order.id,
                        user_id=user_id,
                        role=FulfillmentAssignmentRole.WORKER,
                        created_by_id=self.auth_info.user_id,
                    )
                    order.assignments.append(assignment)

            order = await self.repository.update(order)
            orders.append(order)

        return orders

    async def add_note(
        self,
        order_id: uuid.UUID,
        content: str,
    ) -> FulfillmentOrder:
        order = await self._get_or_raise(order_id)

        await self._log_activity(
            order.id,
            FulfillmentActivityType.NOTE_ADDED,
            content,
        )

        return order

    async def _get_or_raise(self, order_id: uuid.UUID) -> FulfillmentOrder:
        order = await self.repository.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Fulfillment order {order_id} not found")
        return order

    async def _generate_order_number(self) -> str:
        next_number = await self.repository.get_next_order_number()
        return f"FO-{next_number:06d}"

    async def _log_activity(
        self,
        order_id: uuid.UUID,
        activity_type: FulfillmentActivityType,
        content: str,
        metadata: dict | None = None,
    ) -> FulfillmentActivity:
        activity = FulfillmentActivity(
            fulfillment_order_id=order_id,
            activity_type=activity_type,
            content=content,
            metadata=metadata,
            created_by_id=self.auth_info.user_id,
        )
        return await self.activity_repository.create(activity)
```

### 5.2 FulfillmentPickingService

**File:** `app/graphql/v2/core/fulfillment/services/fulfillment_picking_service.py`

```python
import uuid
from datetime import datetime
from decimal import Decimal

from app.core.auth.auth_info import AuthInfo
from app.errors import NotFoundError
from app.graphql.v2.core.fulfillment.repositories.fulfillment_activity_repository import (
    FulfillmentActivityRepository,
)
from app.graphql.v2.core.fulfillment.repositories.fulfillment_line_repository import (
    FulfillmentLineRepository,
)
from app.graphql.v2.core.fulfillment.repositories.fulfillment_order_repository import (
    FulfillmentOrderRepository,
)
from commons.db.v6.fulfillment.enums import (
    FulfillmentActivityType,
    FulfillmentOrderStatus,
)
from commons.db.v6.fulfillment.fulfillment_activity import FulfillmentActivity
from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder
from commons.db.v6.fulfillment.fulfillment_order_line_item import (
    FulfillmentOrderLineItem,
)


class FulfillmentPickingService:
    def __init__(
        self,
        order_repository: FulfillmentOrderRepository,
        line_repository: FulfillmentLineRepository,
        activity_repository: FulfillmentActivityRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.order_repository = order_repository
        self.line_repository = line_repository
        self.activity_repository = activity_repository
        self.auth_info = auth_info

    async def start_picking(self, order_id: uuid.UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.RELEASED:
            raise ValueError("Order must be in RELEASED status to start picking")

        order.status = FulfillmentOrderStatus.PICKING
        order.pick_started_at = datetime.utcnow()

        order = await self.order_repository.update(order)

        await self._log_activity(
            order.id,
            FulfillmentActivityType.PICK_STARTED,
            "Picking started",
        )

        return order

    async def update_picked_quantity(
        self,
        line_item_id: uuid.UUID,
        quantity: Decimal,
        location_id: uuid.UUID | None = None,
        notes: str | None = None,
    ) -> FulfillmentOrderLineItem:
        line_item = await self.line_repository.get_by_id(line_item_id)
        if not line_item:
            raise NotFoundError(f"Line item {line_item_id} not found")

        line_item.picked_qty = quantity
        if location_id:
            line_item.pick_location_id = location_id
        if notes:
            line_item.notes = notes

        return await self.line_repository.update(line_item)

    async def complete_picking(self, order_id: uuid.UUID) -> FulfillmentOrder:
        order = await self._get_order_or_raise(order_id)

        if order.status != FulfillmentOrderStatus.PICKING:
            raise ValueError("Order must be in PICKING status to complete")

        # Check if all items are picked
        all_picked = all(
            item.picked_qty >= item.ordered_qty - item.backorder_qty
            for item in order.line_items
        )

        if not all_picked:
            raise ValueError("Not all items have been picked")

        order.status = FulfillmentOrderStatus.PACKING
        order.pick_completed_at = datetime.utcnow()

        order = await self.order_repository.update(order)

        await self._log_activity(
            order.id,
            FulfillmentActivityType.PICK_COMPLETED,
            "Picking completed",
        )

        return order

    async def report_discrepancy(
        self,
        line_item_id: uuid.UUID,
        actual_quantity: Decimal,
        reason: str,
    ) -> FulfillmentOrder:
        line_item = await self.line_repository.get_by_id(line_item_id)
        if not line_item:
            raise NotFoundError(f"Line item {line_item_id} not found")

        shortage = line_item.ordered_qty - actual_quantity
        if shortage > 0:
            line_item.backorder_qty = shortage
            line_item.short_reason = reason
            line_item.allocated_qty = actual_quantity

            await self.line_repository.update(line_item)

            order = await self._get_order_or_raise(line_item.fulfillment_order_id)
            order.has_backorder_items = True
            order.status = FulfillmentOrderStatus.BACKORDER_REVIEW
            order = await self.order_repository.update(order)

            await self._log_activity(
                order.id,
                FulfillmentActivityType.BACKORDER_REPORTED,
                f"Inventory discrepancy reported: {reason}",
                {"line_item_id": str(line_item_id), "shortage": str(shortage)},
            )

            return order

        return await self._get_order_or_raise(line_item.fulfillment_order_id)

    async def _get_order_or_raise(self, order_id: uuid.UUID) -> FulfillmentOrder:
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Fulfillment order {order_id} not found")
        return order

    async def _log_activity(
        self,
        order_id: uuid.UUID,
        activity_type: FulfillmentActivityType,
        content: str,
        metadata: dict | None = None,
    ) -> FulfillmentActivity:
        activity = FulfillmentActivity(
            fulfillment_order_id=order_id,
            activity_type=activity_type,
            content=content,
            metadata=metadata,
            created_by_id=self.auth_info.user_id,
        )
        return await self.activity_repository.create(activity)
```

---

## 6. Repository Layer

### 6.1 FulfillmentOrderRepository

**File:** `app/graphql/v2/core/fulfillment/repositories/fulfillment_order_repository.py`

```python
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload

from app.graphql.base_repository import BaseRepository
from commons.db.v6.fulfillment.enums import FulfillmentOrderStatus
from commons.db.v6.fulfillment.fulfillment_order import FulfillmentOrder


class FulfillmentOrderRepository(BaseRepository[FulfillmentOrder]):
    async def get_by_id(self, order_id: uuid.UUID) -> FulfillmentOrder | None:
        stmt = (
            select(FulfillmentOrder)
            .options(
                joinedload(FulfillmentOrder.warehouse),
                joinedload(FulfillmentOrder.carrier),
                selectinload(FulfillmentOrder.line_items),
                selectinload(FulfillmentOrder.packing_boxes),
                selectinload(FulfillmentOrder.assignments),
                selectinload(FulfillmentOrder.activities),
            )
            .where(FulfillmentOrder.id == order_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_orders(
        self,
        warehouse_id: uuid.UUID | None = None,
        status: list[int] | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FulfillmentOrder]:
        stmt = select(FulfillmentOrder).options(
            joinedload(FulfillmentOrder.warehouse),
            selectinload(FulfillmentOrder.line_items),
        )

        if warehouse_id:
            stmt = stmt.where(FulfillmentOrder.warehouse_id == warehouse_id)

        if status:
            stmt = stmt.where(FulfillmentOrder.status.in_(status))

        if search:
            stmt = stmt.where(
                FulfillmentOrder.fulfillment_order_number.ilike(f"%{search}%")
            )

        stmt = stmt.order_by(FulfillmentOrder.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_stats(self, warehouse_id: uuid.UUID | None = None) -> dict[str, int]:
        base_query = select(func.count(FulfillmentOrder.id))

        if warehouse_id:
            base_query = base_query.where(
                FulfillmentOrder.warehouse_id == warehouse_id
            )

        pending = await self.session.execute(
            base_query.where(FulfillmentOrder.status == FulfillmentOrderStatus.PENDING)
        )

        in_progress_statuses = [
            FulfillmentOrderStatus.RELEASED,
            FulfillmentOrderStatus.PICKING,
            FulfillmentOrderStatus.PACKING,
            FulfillmentOrderStatus.SHIPPING,
        ]
        in_progress = await self.session.execute(
            base_query.where(FulfillmentOrder.status.in_(in_progress_statuses))
        )

        completed_statuses = [
            FulfillmentOrderStatus.SHIPPED,
            FulfillmentOrderStatus.DELIVERED,
            FulfillmentOrderStatus.COMMUNICATED,
        ]
        completed = await self.session.execute(
            base_query.where(FulfillmentOrder.status.in_(completed_statuses))
        )

        backorder = await self.session.execute(
            base_query.where(
                FulfillmentOrder.status == FulfillmentOrderStatus.BACKORDER_REVIEW
            )
        )

        return {
            "pending": pending.scalar() or 0,
            "in_progress": in_progress.scalar() or 0,
            "completed": completed.scalar() or 0,
            "backorder": backorder.scalar() or 0,
        }

    async def get_next_order_number(self) -> int:
        stmt = select(func.coalesce(func.max(FulfillmentOrder.id), 0) + 1)
        result = await self.session.execute(stmt)
        return result.scalar() or 1
```

---

## 7. Alembic Migrations

**File:** `alembic/versions/xxxx_add_fulfillment_tables.py`

```python
"""Add fulfillment tables

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-xx-xx

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "xxxx"
down_revision: str | None = "previous_revision"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Fulfillment Orders
    op.create_table(
        "fulfillment_orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fulfillment_order_number", sa.String(50), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=False),
        sa.Column("carrier_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False, default=1),
        sa.Column("fulfillment_method", sa.Integer(), nullable=False, default=1),
        sa.Column("carrier_type", sa.Integer(), nullable=True),
        sa.Column("ship_to_customer_id", sa.UUID(), nullable=True),
        sa.Column("ship_to_address", postgresql.JSONB(), nullable=True),
        sa.Column("need_by_date", sa.Date(), nullable=True),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.Column("pick_started_at", sa.DateTime(), nullable=True),
        sa.Column("pick_completed_at", sa.DateTime(), nullable=True),
        sa.Column("pack_completed_at", sa.DateTime(), nullable=True),
        sa.Column("ship_confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("tracking_numbers", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("bol_number", sa.String(100), nullable=True),
        sa.Column("pro_number", sa.String(100), nullable=True),
        sa.Column("pickup_signature", sa.Text(), nullable=True),
        sa.Column("pickup_timestamp", sa.DateTime(), nullable=True),
        sa.Column("pickup_customer_name", sa.String(255), nullable=True),
        sa.Column("driver_name", sa.String(255), nullable=True),
        sa.Column("has_backorder_items", sa.Boolean(), nullable=False, default=False),
        sa.Column("hold_reason", sa.Text(), nullable=True),
        sa.Column("backorder_review_data", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["pycommission.orders.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["pywarehouse.warehouses.id"]),
        sa.ForeignKeyConstraint(["carrier_id"], ["pywarehouse.shipping_carriers.id"]),
        sa.ForeignKeyConstraint(["ship_to_customer_id"], ["pycrm.customers.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["pycrm.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_orders_order_id",
        "fulfillment_orders",
        ["order_id"],
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_orders_warehouse_id",
        "fulfillment_orders",
        ["warehouse_id"],
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_orders_status",
        "fulfillment_orders",
        ["status"],
        schema="pywarehouse",
    )
    op.create_unique_constraint(
        "uq_fulfillment_order_number",
        "fulfillment_orders",
        ["fulfillment_order_number"],
        schema="pywarehouse",
    )

    # Fulfillment Order Line Items
    op.create_table(
        "fulfillment_order_line_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fulfillment_order_id", sa.UUID(), nullable=False),
        sa.Column("order_detail_id", sa.UUID(), nullable=True),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("ordered_qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("allocated_qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("picked_qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("packed_qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("shipped_qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("backorder_qty", sa.Numeric(18, 4), nullable=False),
        sa.Column("fulfilled_by_manufacturer", sa.Boolean(), nullable=False),
        sa.Column("manufacturer_fulfillment_status", sa.String(50), nullable=True),
        sa.Column("linked_shipment_request_id", sa.UUID(), nullable=True),
        sa.Column("pick_location_id", sa.UUID(), nullable=True),
        sa.Column("short_reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["order_detail_id"], ["pycommission.order_details.id"]
        ),
        sa.ForeignKeyConstraint(["product_id"], ["pycrm.products.id"]),
        sa.ForeignKeyConstraint(
            ["pick_location_id"], ["pywarehouse.warehouse_locations.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_line_items_order_id",
        "fulfillment_order_line_items",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Fulfillment Assignments
    op.create_table(
        "fulfillment_assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fulfillment_order_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["pycrm.users.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["pycrm.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_assignments_order_id",
        "fulfillment_assignments",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Fulfillment Activities
    op.create_table(
        "fulfillment_activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fulfillment_order_id", sa.UUID(), nullable=False),
        sa.Column("activity_type", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["pycrm.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_activities_order_id",
        "fulfillment_activities",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Packing Boxes
    op.create_table(
        "packing_boxes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fulfillment_order_id", sa.UUID(), nullable=False),
        sa.Column("container_type_id", sa.UUID(), nullable=True),
        sa.Column("box_number", sa.Integer(), nullable=False),
        sa.Column("length", sa.Numeric(10, 2), nullable=True),
        sa.Column("width", sa.Numeric(10, 2), nullable=True),
        sa.Column("height", sa.Numeric(10, 2), nullable=True),
        sa.Column("weight", sa.Numeric(10, 2), nullable=True),
        sa.Column("tracking_number", sa.String(100), nullable=True),
        sa.Column("label_printed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["container_type_id"], ["pywarehouse.container_types.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_packing_boxes_order_id",
        "packing_boxes",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Packing Box Items
    op.create_table(
        "packing_box_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("packing_box_id", sa.UUID(), nullable=False),
        sa.Column("fulfillment_line_item_id", sa.UUID(), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.ForeignKeyConstraint(
            ["packing_box_id"],
            ["pywarehouse.packing_boxes.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["fulfillment_line_item_id"],
            ["pywarehouse.fulfillment_order_line_items.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_packing_box_items_box_id",
        "packing_box_items",
        ["packing_box_id"],
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_table("packing_box_items", schema="pywarehouse")
    op.drop_table("packing_boxes", schema="pywarehouse")
    op.drop_table("fulfillment_activities", schema="pywarehouse")
    op.drop_table("fulfillment_assignments", schema="pywarehouse")
    op.drop_table("fulfillment_order_line_items", schema="pywarehouse")
    op.drop_table("fulfillment_orders", schema="pywarehouse")
```

---

## 8. Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)

1. **Create Models in flowbot-commons**
   - `FulfillmentOrder`
   - `FulfillmentOrderLineItem`
   - `FulfillmentAssignment`
   - `FulfillmentActivity`
   - All enums

2. **Create Alembic Migration**
   - All 6 tables with proper FKs and indexes

3. **Create Base Repository & Service**
   - `FulfillmentOrderRepository`
   - `FulfillmentOrderService`

4. **Create GraphQL Types**
   - Response types
   - Input types
   - Enums

5. **Create Basic Queries & Mutations**
   - `fulfillment_orders` query
   - `fulfillment_order` query
   - `create_fulfillment_order` mutation

### Phase 2: Workflow Implementation (Week 3-4)

1. **Picking Flow**
   - `FulfillmentPickingService`
   - `start_picking` mutation
   - `update_picked_quantity` mutation
   - `complete_picking` mutation
   - `report_inventory_discrepancy` mutation

2. **Packing Flow**
   - `FulfillmentPackingService`
   - `PackingBox` models
   - Box CRUD mutations
   - Item assignment mutations
   - `complete_packing` mutation

3. **Shipping Flow**
   - `FulfillmentShippingService`
   - `complete_shipping` mutation
   - `mark_delivered` mutation

### Phase 3: Backorder & Advanced Features (Week 5-6)

1. **Backorder Handling**
   - `FulfillmentBackorderService`
   - `mark_manufacturer_direct` mutation
   - `split_fulfillment_line_item` mutation
   - `cancel_backorder_items` mutation

2. **Bulk Operations**
   - `bulk_assign_fulfillment_orders` mutation
   - Stats aggregation queries

3. **Activity Logging**
   - Complete activity tracking
   - Notes system

### Phase 4: Integration & Polish (Week 7-8)

1. **Factory for Order Creation**
   - Create fulfillment from Order automatically
   - Line item mapping from OrderDetail

2. **Inventory Integration**
   - Link to `LocationProductAssignment`
   - Multi-location picking support

3. **Frontend Integration**
   - Replace mock functions with GraphQL calls
   - Test end-to-end workflows

---

## 9. Testing Strategy

### Unit Tests

```python
# tests/graphql/v2/core/fulfillment/test_fulfillment_order_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.graphql.v2.core.fulfillment.services.fulfillment_order_service import (
    FulfillmentOrderService,
)
from commons.db.v6.fulfillment.enums import FulfillmentOrderStatus


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def mock_activity_repository():
    return AsyncMock()


@pytest.fixture
def mock_auth_info():
    auth = MagicMock()
    auth.user_id = "test-user-id"
    return auth


@pytest.fixture
def service(mock_repository, mock_activity_repository, mock_auth_info):
    return FulfillmentOrderService(
        repository=mock_repository,
        activity_repository=mock_activity_repository,
        auth_info=mock_auth_info,
    )


async def test_release_to_warehouse_success(service, mock_repository):
    order = MagicMock()
    order.status = FulfillmentOrderStatus.PENDING
    order.id = "test-order-id"
    order.assignments = []

    mock_repository.get_by_id.return_value = order
    mock_repository.update.return_value = order

    result = await service.release_to_warehouse("test-order-id")

    assert result.status == FulfillmentOrderStatus.RELEASED
    assert result.released_at is not None


async def test_release_to_warehouse_wrong_status(service, mock_repository):
    order = MagicMock()
    order.status = FulfillmentOrderStatus.PICKING

    mock_repository.get_by_id.return_value = order

    with pytest.raises(ValueError, match="PENDING"):
        await service.release_to_warehouse("test-order-id")
```

### Integration Tests

```python
# tests/graphql/v2/core/fulfillment/test_fulfillment_integration.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_fulfillment_workflow(client: AsyncClient, auth_headers: dict):
    # Create fulfillment order
    create_response = await client.post(
        "/graphql",
        json={
            "query": """
                mutation CreateFulfillmentOrder($input: CreateFulfillmentOrderInput!) {
                    createFulfillmentOrder(input: $input) {
                        id
                        status
                        fulfillmentOrderNumber
                    }
                }
            """,
            "variables": {
                "input": {
                    "orderId": "test-order-id",
                    "warehouseId": "test-warehouse-id",
                }
            },
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 200
    data = create_response.json()["data"]["createFulfillmentOrder"]
    assert data["status"] == "PENDING"

    fulfillment_id = data["id"]

    # Release to warehouse
    release_response = await client.post(
        "/graphql",
        json={
            "query": """
                mutation ReleaseToWarehouse($id: UUID!) {
                    releaseToWarehouse(id: $id) {
                        id
                        status
                        releasedAt
                    }
                }
            """,
            "variables": {"id": fulfillment_id},
        },
        headers=auth_headers,
    )

    assert release_response.status_code == 200
    data = release_response.json()["data"]["releaseToWarehouse"]
    assert data["status"] == "RELEASED"
    assert data["releasedAt"] is not None
```

---

## Appendix A: File Size Guidelines

Per CLAUDE.md requirements, each file should be under 300 lines. Split services as follows:

| Service | Responsibility | Max Lines |
|---------|----------------|-----------|
| `fulfillment_order_service.py` | CRUD, release, cancel, notes | ~200 |
| `fulfillment_picking_service.py` | Start, update, complete picking | ~150 |
| `fulfillment_packing_service.py` | Box CRUD, item assignment | ~150 |
| `fulfillment_shipping_service.py` | Complete shipping, delivery | ~100 |
| `fulfillment_backorder_service.py` | Manufacturer direct, split, cancel | ~150 |

---

## Appendix B: GraphQL Schema Summary

```graphql
type Query {
  fulfillmentOrders(
    warehouseId: UUID
    status: [FulfillmentOrderStatus!]
    search: String
    limit: Int
    offset: Int
  ): [FulfillmentOrderResponse!]!

  fulfillmentOrder(id: UUID!): FulfillmentOrderResponse

  fulfillmentStats(warehouseId: UUID): FulfillmentStatsResponse!
}

type Mutation {
  # Order Lifecycle
  createFulfillmentOrder(input: CreateFulfillmentOrderInput!): FulfillmentOrderResponse!
  updateFulfillmentOrder(id: UUID!, input: UpdateFulfillmentOrderInput!): FulfillmentOrderResponse!
  releaseToWarehouse(id: UUID!): FulfillmentOrderResponse!
  cancelFulfillmentOrder(id: UUID!, reason: String!): FulfillmentOrderResponse!

  # Assignments
  bulkAssignFulfillmentOrders(input: BulkAssignmentInput!): [FulfillmentOrderResponse!]!

  # Picking
  startPicking(id: UUID!): FulfillmentOrderResponse!
  updatePickedQuantity(input: UpdatePickedQuantityInput!): FulfillmentOrderLineItemResponse!
  completePicking(id: UUID!): FulfillmentOrderResponse!
  reportInventoryDiscrepancy(lineItemId: UUID!, actualQuantity: Decimal!, reason: String!): FulfillmentOrderResponse!

  # Packing
  addPackingBox(fulfillmentOrderId: UUID!, containerTypeId: UUID): PackingBoxResponse!
  updatePackingBox(boxId: UUID!, length: Decimal, width: Decimal, height: Decimal, weight: Decimal): PackingBoxResponse!
  assignItemToBox(input: AssignItemToBoxInput!): PackingBoxResponse!
  removeItemFromBox(boxId: UUID!, lineItemId: UUID!): PackingBoxResponse!
  deletePackingBox(boxId: UUID!): Boolean!
  completePacking(id: UUID!): FulfillmentOrderResponse!

  # Shipping
  completeShipping(id: UUID!, input: CompleteShippingInput!): FulfillmentOrderResponse!
  markDelivered(id: UUID!): FulfillmentOrderResponse!

  # Backorder
  markManufacturerDirect(fulfillmentOrderId: UUID!, lineItemIds: [UUID!]!): FulfillmentOrderResponse!
  splitFulfillmentLineItem(lineItemId: UUID!, warehouseQty: Decimal!, manufacturerQty: Decimal!): FulfillmentOrderLineItemResponse!
  cancelBackorderItems(fulfillmentOrderId: UUID!, lineItemIds: [UUID!]!, reason: String!): FulfillmentOrderResponse!

  # Notes
  addFulfillmentNote(fulfillmentOrderId: UUID!, content: String!): FulfillmentOrderResponse!
}
```

---

## Appendix C: Status Transition Rules

```
PENDING → RELEASED (releaseToWarehouse)
PENDING → CANCELLED (cancelFulfillmentOrder)

RELEASED → PICKING (startPicking)
RELEASED → CANCELLED (cancelFulfillmentOrder)

PICKING → PACKING (completePicking)
PICKING → BACKORDER_REVIEW (reportInventoryDiscrepancy)
PICKING → CANCELLED (cancelFulfillmentOrder)

BACKORDER_REVIEW → PICKING (after resolution)
BACKORDER_REVIEW → CANCELLED (cancelBackorderItems - all items)

PACKING → SHIPPING (completePacking)
PACKING → CANCELLED (cancelFulfillmentOrder)

SHIPPING → SHIPPED (completeShipping)
SHIPPING → PARTIAL_SHIPPED (completeShipping - partial)

SHIPPED → DELIVERED (markDelivered)
SHIPPED → COMMUNICATED (sendShipmentConfirmation)

COMMUNICATED → DELIVERED (markDelivered)
```
