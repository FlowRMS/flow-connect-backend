import strawberry


@strawberry.type
class ProductImportError:
    factory_part_number: str
    error: str
