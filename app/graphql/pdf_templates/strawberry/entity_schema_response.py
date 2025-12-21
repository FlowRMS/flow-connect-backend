
import strawberry


@strawberry.type
class EntityField:


    name: str
    type: str 
    nullable: bool
    description: str | None = None


@strawberry.type
class EntitySchema:

    entity_name: str
    display_name: str
    fields: list[EntityField]
    related_entities: list[str] = strawberry.field(
        default_factory=list
    ) 


@strawberry.type
class EntitySchemasResponse:

    entities: list[EntitySchema]

