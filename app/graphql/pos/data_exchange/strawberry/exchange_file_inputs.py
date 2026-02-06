import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class UploadExchangeFileInput:
    files: list[Upload]
    reporting_period: str
    is_pos: bool
    is_pot: bool
    target_org_ids: list[strawberry.ID]
