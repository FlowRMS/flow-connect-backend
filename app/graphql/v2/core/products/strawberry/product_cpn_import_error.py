import strawberry


@strawberry.type
class ProductCpnImportError:
    factory_part_number: str
    customer_name: str
    error: str
