from uuid import UUID

import strawberry
from commons.db.v6 import WarehouseSettings

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class WarehouseSettingsInput(BaseInputGQL[WarehouseSettings]):
    warehouse_id: UUID
    auto_generate_codes: bool = False
    require_location: bool = True
    show_in_pick_lists: bool = True
    generate_qr_codes: bool = False

    def to_orm_model(self) -> WarehouseSettings:
        return WarehouseSettings(
            warehouse_id=self.warehouse_id,
            auto_generate_codes=self.auto_generate_codes,
            require_location=self.require_location,
            show_in_pick_lists=self.show_in_pick_lists,
            generate_qr_codes=self.generate_qr_codes,
        )
