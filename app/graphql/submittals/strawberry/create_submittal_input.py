from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalStatus,
    TransmittalPurpose,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    SubmittalStatusGQL,
    TransmittalPurposeGQL,
)
from app.graphql.submittals.strawberry.submittal_config_input import (
    SubmittalConfigInput,
)


@strawberry.input
class CreateSubmittalInput(BaseInputGQL[Submittal]):
    submittal_number: str
    quote_id: UUID | None = None
    job_id: UUID | None = None
    status: SubmittalStatusGQL = SubmittalStatusGQL.DRAFT
    transmittal_purpose: TransmittalPurposeGQL | None = None
    description: str | None = None
    config: SubmittalConfigInput | None = None

    def to_orm_model(self) -> Submittal:
        config = self.config or SubmittalConfigInput()
        return Submittal(
            submittal_number=self.submittal_number,
            quote_id=self.quote_id,
            job_id=self.job_id,
            status=SubmittalStatus(self.status.value),
            transmittal_purpose=(
                TransmittalPurpose(self.transmittal_purpose.value)
                if self.transmittal_purpose
                else None
            ),
            description=self.description,
            config_include_lamps=config.include_lamps,
            config_include_accessories=config.include_accessories,
            config_include_cq=config.include_cq,
            config_include_from_orders=config.include_from_orders,
            config_roll_up_kits=config.roll_up_kits,
            config_roll_up_accessories=config.roll_up_accessories,
            config_include_zero_quantity_items=config.include_zero_quantity_items,
            config_drop_descriptions=config.drop_descriptions,
            config_drop_line_notes=config.drop_line_notes,
        )
