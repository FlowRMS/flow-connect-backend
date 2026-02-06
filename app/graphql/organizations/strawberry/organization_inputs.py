import strawberry


@strawberry.input
class PosContactInput:
    email: str


@strawberry.input
class CreateOrganizationInput:
    name: str
    domain: str
    contact: PosContactInput | None = None
