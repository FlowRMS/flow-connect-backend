# Document Execution Workflow

This module handles the execution of approved `PendingDocument` records, converting extracted DTOs into domain entities (Orders, Quotes, Invoices, etc.) using the existing service layer.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GraphQL Layer                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Mutation: executeWorkflow(pendingDocumentId: UUID)          ││
│  │   → Kicks off TaskIQ background task                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TaskIQ Worker                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ execute_pending_document_task(pending_id, tenant)           ││
│  │   1. Fetch PendingDocument + PendingEntities                ││
│  │   2. DocumentExecutorService.execute()                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DocumentExecutorService                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Build entity_mapping from confirmed PendingEntities      ││
│  │ 2. Parse DTOs from extracted_data_json                      ││
│  │ 3. Get converter for entity_type (with session)             ││
│  │ 4. For each DTO: await converter.to_input() → create entity ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Entity Converters                              │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────────┐   │
│  │OrderConverter  │ │QuoteConverter  │ │InvoiceConverter    │   │
│  │DTO → Input     │ │DTO → Input     │ │DTO → Input         │   │
│  │ + factory info │ │ + factory info │ │ + factory info     │   │
│  └────────────────┘ └────────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
app/workers/document_execution/
├── __init__.py
├── README.md                    # This file
├── task.py                      # TaskIQ background task
├── executor_service.py          # Main orchestration service
└── converters/
    ├── __init__.py
    ├── base.py                  # Abstract base converter with factory helpers
    ├── registry.py              # Converter registry (simple dict mapping)
    └── order_converter.py       # OrderDTO → OrderInput converter
```

## How It Works

### 1. GraphQL Mutation Triggers the Workflow

```graphql
mutation {
  executeWorkflow(pendingDocumentId: "uuid-here") {
    success
    taskId
    message
  }
}
```

The mutation (`app/graphql/documents/mutations/documents_mutations.py`) kicks off a background TaskIQ task with the document ID and tenant name.

### 2. TaskIQ Worker Fetches the Document

The worker task (`task.py`) runs in the background:
- Connects to the tenant's database
- Fetches the `PendingDocument` with its `pending_entities`
- Passes it to `DocumentExecutorService`

### 3. Entity Mapping from Confirmed Entities

The `DocumentExecutorService` builds a mapping from confirmed `PendingEntity` records:

```python
entity_mapping = {
    "factory": UUID("..."),           # From EntityPendingType.FACTORIES
    "sold_to_customer": UUID("..."),  # From EntityPendingType.CUSTOMERS
    "bill_to_customer": UUID("..."),  # From EntityPendingType.BILL_TO_CUSTOMERS
    "product_0": UUID("..."),         # From EntityPendingType.PRODUCTS (index 0)
    "product_1": UUID("..."),         # From EntityPendingType.PRODUCTS (index 1)
    "end_user_0": UUID("..."),        # From EntityPendingType.END_USERS (index 0)
}
```

Only entities with these confirmation statuses are included:
- `CONFIRMED` - User explicitly confirmed the match
- `AUTO_MATCHED` - AI found a high-confidence match
- `CREATED_NEW` - User created a new entity

### 4. DTO Parsing

The service parses DTOs from `PendingDocument.extracted_data_json`:

```python
# extracted_data_json format for PDFs:
{
    "data": [
        {"order_number": "PO-123", "factory": {...}, "details": [...]}
    ]
}
```

Each raw dict is validated into the appropriate DTO (e.g., `OrderDTO`).

### 5. Converter Transforms DTO to Input

The converter uses the entity mapping to create a Strawberry input. Each converter:
- Receives the `AsyncSession` in its constructor
- Can fetch factory info for default commission rates
- Is async to allow database lookups

```python
OrderDTO + entity_mapping → OrderInput
```

Key transformations:
- `dto.factory` → `entity_mapping["factory"]` (UUID)
- `dto.sold_to_customer` → `entity_mapping["sold_to_customer"]` (UUID)
- `dto.details[0].end_user` → `entity_mapping["end_user_0"]` or fallback to sold_to_customer
- Missing `commission_rate` → fetch from factory's `base_commission_rate`
- Missing `commission_discount_rate` → fetch from factory's `commission_discount_rate`
- Missing `discount_rate` → fetch from factory's `overall_discount_rate`
- Missing products → adhoc product name from part number

### 6. Entity Creation

The executor creates the domain entity:
- Calculates balance (for Orders)
- Persists to database via session
- Returns created entity ID

## Base Converter Features

The `BaseEntityConverter` provides common functionality:

```python
class BaseEntityConverter(ABC, Generic[TDto, TInput]):
    entity_type: EntityType  # Class attribute for the entity type

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._factory_cache: dict[UUID, Factory] = {}  # Cached factory lookups

    # Factory helper methods
    async def get_factory(self, factory_id: UUID) -> Factory | None
    async def get_factory_commission_rate(self, factory_id: UUID) -> Decimal
    async def get_factory_commission_discount_rate(self, factory_id: UUID) -> Decimal
    async def get_factory_discount_rate(self, factory_id: UUID) -> Decimal

    # Abstract method to implement
    @abstractmethod
    async def to_input(self, dto: TDto, entity_mapping: dict[str, UUID]) -> TInput
```

## Extending the System

### Adding a New Entity Type (e.g., Quote)

#### Step 1: Create the Converter

```python
# app/workers/document_execution/converters/quote_converter.py
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from commons.db.v6.ai.documents.enums import EntityType
from commons.dtos.quote.quote_dto import QuoteDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.quotes.strawberry.quote_input import QuoteInput
from app.graphql.quotes.strawberry.quote_detail_input import QuoteDetailInput

from .base import BaseEntityConverter


class QuoteConverter(BaseEntityConverter[QuoteDTO, QuoteInput]):
    entity_type = EntityType.QUOTES

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def to_input(
        self,
        dto: QuoteDTO,
        entity_mapping: dict[str, UUID],
    ) -> QuoteInput:
        factory_id = entity_mapping.get("factory")
        sold_to_id = entity_mapping.get("sold_to_customer")

        if not factory_id:
            raise ValueError("Factory ID required")
        if not sold_to_id:
            raise ValueError("Sold-to customer ID required")

        # Get factory defaults for rates not in DTO
        default_commission = await self.get_factory_commission_rate(factory_id)
        default_discount = await self.get_factory_discount_rate(factory_id)

        return QuoteInput(
            quote_number=dto.quote_number or self._generate_quote_number(),
            entity_date=dto.quote_date or date.today(),
            valid_until=dto.valid_until or date.today(),
            sold_to_customer_id=sold_to_id,
            factory_id=factory_id,
            details=[
                self._convert_detail(d, entity_mapping, sold_to_id, default_commission, default_discount)
                for d in dto.details
            ],
        )

    def _convert_detail(
        self,
        dto_detail,
        entity_mapping: dict[str, UUID],
        fallback_end_user_id: UUID,
        default_commission: Decimal,
        default_discount: Decimal,
    ) -> QuoteDetailInput:
        flow_index = dto_detail.flow_index
        product_id = entity_mapping.get(f"product_{flow_index}")
        end_user_id = entity_mapping.get(f"end_user_{flow_index}") or fallback_end_user_id

        return QuoteDetailInput(
            item_number=dto_detail.item_number or 1,
            quantity=Decimal(str(dto_detail.quantity or 1)),
            unit_price=dto_detail.unit_price or Decimal("0"),
            end_user_id=end_user_id,
            product_id=product_id,
            product_name_adhoc=dto_detail.factory_part_number if not product_id else None,
            commission_rate=dto_detail.commission_rate or default_commission,
            discount_rate=dto_detail.discount_rate or default_discount,
        )

    @staticmethod
    def _generate_quote_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"AUTO-Q-{timestamp}"
```

#### Step 2: Register the Converter

Update `converters/registry.py`:

```python
from commons.db.v6.ai.documents.enums import EntityType

from .order_converter import OrderConverter
from .quote_converter import QuoteConverter  # ADD THIS

CONVERTER_REGISTRY: dict[EntityType, type[BaseEntityConverter]] = {
    EntityType.ORDERS: OrderConverter,
    EntityType.QUOTES: QuoteConverter,  # ADD THIS
}
```

#### Step 3: Add DTO Parsing

Update `executor_service.py`:

```python
def _parse_dtos(self, pending_document: PendingDocument) -> list[Any]:
    if not pending_document.extracted_data_json:
        return []

    raw_dtos = BaseEntityConverter.parse_dtos_from_json(
        pending_document.extracted_data_json
    )

    match pending_document.entity_type:
        case EntityType.ORDERS:
            return [OrderDTO.model_validate(d) for d in raw_dtos]
        case EntityType.QUOTES:  # ADD THIS
            return [QuoteDTO.model_validate(d) for d in raw_dtos]
        case _:
            raise ValueError(f"Unsupported entity type: {pending_document.entity_type}")
```

#### Step 4: Add Entity Creation

Update `executor_service.py`:

```python
async def _create_entity(
    self,
    entity_type: EntityType,
    converter: BaseEntityConverter[Any, Any],
    dto: Any,
    entity_mapping: dict[str, UUID],
) -> UUID:
    input_obj = await converter.to_input(dto, entity_mapping)

    match entity_type:
        case EntityType.ORDERS:
            return await self._create_order(input_obj)
        case EntityType.QUOTES:  # ADD THIS
            return await self._create_quote(input_obj)
        case _:
            raise ValueError(f"Unsupported entity type: {entity_type}")

async def _create_quote(self, quote_input: Any) -> UUID:  # ADD THIS
    quote: Quote = quote_input.to_orm_model()
    balance = self._calculate_quote_balance(quote)
    self.session.add(balance)
    await self.session.flush([balance])

    quote.balance_id = balance.id
    self.session.add(quote)
    await self.session.flush([quote])

    logger.info(f"Created quote: {quote.id} ({quote.quote_number})")
    return quote.id
```

## Entity Mapping Keys

| PendingEntity Type | Mapping Key | Description |
|---|---|---|
| `FACTORIES` | `"factory"` | Factory UUID |
| `CUSTOMERS` | `"sold_to_customer"` | Sold-to customer UUID |
| `BILL_TO_CUSTOMERS` | `"bill_to_customer"` | Bill-to customer UUID |
| `PRODUCTS` | `"product_{index}"` | Product UUID for line item at index |
| `END_USERS` | `"end_user_{index}"` | End user UUID for line item at index |

## Default Behaviors

| Scenario | Default Behavior |
|---|---|
| Missing `order_number` | Generate `AUTO-{timestamp}` |
| Missing `entity_date` | Use `date.today()` |
| Missing `due_date` | Use `entity_date` |
| Missing end user for line | Fallback to sold-to customer |
| Product not confirmed | Use adhoc product name from part number |
| Missing `commission_rate` | Use factory's `base_commission_rate` |
| Missing `commission_discount_rate` | Use factory's `commission_discount_rate` |
| Missing `discount_rate` | Use factory's `overall_discount_rate` |

## Transaction Scope

All entity creation happens within a single database transaction. If any entity fails to create, the entire transaction is rolled back (all-or-nothing).

## Error Handling

Errors are logged and returned in the task result:

```python
{
    "status": "error",
    "error": "Error message here"
}
```

Successful execution returns:

```python
{
    "status": "success",
    "created_entity_ids": ["uuid1", "uuid2"],
    "count": 2
}
```
