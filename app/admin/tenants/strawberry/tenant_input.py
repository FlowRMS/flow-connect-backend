import strawberry


@strawberry.input
class CreateTenantInput:
    name: str
    owner_email: str
