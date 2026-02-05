from typing import Self

import strawberry
from commons.db.v6.crm.submittals import Submittal

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class SubmittalConfigResponse(DTOMixin[Submittal]):
    include_lamps: bool
    include_accessories: bool
    include_cq: bool
    include_from_orders: bool
    roll_up_kits: bool
    roll_up_accessories: bool
    include_zero_quantity_items: bool
    drop_descriptions: bool
    drop_line_notes: bool

    @classmethod
    def from_orm_model(cls, model: Submittal) -> Self:
        return cls(
            include_lamps=model.config_include_lamps,
            include_accessories=model.config_include_accessories,
            include_cq=model.config_include_cq,
            include_from_orders=model.config_include_from_orders,
            roll_up_kits=model.config_roll_up_kits,
            roll_up_accessories=model.config_roll_up_accessories,
            include_zero_quantity_items=model.config_include_zero_quantity_items,
            drop_descriptions=model.config_drop_descriptions,
            drop_line_notes=model.config_drop_line_notes,
        )
