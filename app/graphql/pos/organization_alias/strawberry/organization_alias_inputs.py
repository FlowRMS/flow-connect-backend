import strawberry


@strawberry.input
class CreateOrganizationAliasInput:
    connected_org_id: strawberry.ID
    alias: str
