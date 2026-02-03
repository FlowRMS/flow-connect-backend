from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalItemChange

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.strawberry.enums import ItemChangeStatusGQL


@strawberry.type
class SubmittalItemChangeResponse(DTOMixin[SubmittalItemChange]):
    _instance: strawberry.Private[SubmittalItemChange]
    id: UUID
    change_analysis_id: UUID
    item_id: UUID | None
    fixture_type: str
    catalog_number: str
    manufacturer: str
    status: ItemChangeStatusGQL
    notes: list[str] | None
    page_references: list[int] | None
    resolved: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, model: SubmittalItemChange) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            change_analysis_id=model.change_analysis_id,
            item_id=model.item_id,
            fixture_type=model.fixture_type,
            catalog_number=model.catalog_number,
            manufacturer=model.manufacturer,
            status=ItemChangeStatusGQL(model.status.value),
            notes=model.notes,
            page_references=model.page_references,
            resolved=model.resolved,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
