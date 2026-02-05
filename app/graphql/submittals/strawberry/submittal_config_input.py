import strawberry
from commons.db.v6.crm.submittals import Submittal

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class SubmittalConfigInput(BaseInputGQL[Submittal]):
    include_lamps: bool = False
    include_accessories: bool = False
    include_cq: bool = False
    include_from_orders: bool = False
    roll_up_kits: bool = False
    roll_up_accessories: bool = True
    include_zero_quantity_items: bool = True
    drop_descriptions: bool = False
    drop_line_notes: bool = True
