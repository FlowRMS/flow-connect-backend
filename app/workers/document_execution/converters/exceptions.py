from uuid import UUID


class ConversionError(Exception):
    pass


class FactoryRequiredError(ConversionError):
    def __init__(self) -> None:
        super().__init__("Factory ID is required but not found in entity_mapping")


class SoldToCustomerRequiredError(ConversionError):
    def __init__(self) -> None:
        super().__init__(
            "Sold-to customer ID is required but not found in entity_mapping"
        )


class OrderRequiredError(ConversionError):
    def __init__(self) -> None:
        super().__init__("Order ID is required but not found in entity_mapping")


class EndUserRequiredError(ConversionError):
    def __init__(self, flow_index: int | None) -> None:
        self.flow_index = flow_index
        super().__init__(f"End user ID is required for detail at index {flow_index}")


class FactoryPartNumberRequiredError(ConversionError):
    def __init__(self, product_description: str | None = None) -> None:
        self.product_description = product_description
        desc = f" for product '{product_description}'" if product_description else ""
        super().__init__(f"Factory part number is required{desc}")


class ProductNotFoundError(ConversionError):
    def __init__(self, flow_index: int | None, fpn: str | None = None) -> None:
        self.flow_index = flow_index
        self.fpn = fpn
        if fpn:
            super().__init__(f"Product '{fpn}' not found at index {flow_index}")
        else:
            super().__init__(f"Product not found at index {flow_index}")


class InvoiceNotFoundError(ConversionError):
    def __init__(self, invoice_number: str, factory_id: UUID) -> None:
        self.invoice_number = invoice_number
        self.factory_id = factory_id
        super().__init__(
            f"Invoice '{invoice_number}' not found for factory {factory_id}"
        )


class CreditCreationFailedError(ConversionError):
    def __init__(self, detail_index: int, reason: str) -> None:
        self.detail_index = detail_index
        self.reason = reason
        super().__init__(
            f"Failed to create credit for detail at index {detail_index}: {reason}"
        )


class AdjustmentCreationFailedError(ConversionError):
    def __init__(self, detail_index: int, reason: str) -> None:
        self.detail_index = detail_index
        self.reason = reason
        super().__init__(
            f"Failed to create adjustment for detail at index {detail_index}: {reason}"
        )


class DeliveryVendorRequiredError(ConversionError):
    def __init__(self) -> None:
        super().__init__("Vendor ID is required but not found in entity_mapping")


class DeliveryWarehouseRequiredError(ConversionError):
    def __init__(self) -> None:
        super().__init__("Warehouse ID is required but not provided in the DTO")


class DeliveryProductRequiredError(ConversionError):
    def __init__(self, flow_index: int | None, part_number: str) -> None:
        self.flow_index = flow_index
        self.part_number = part_number
        super().__init__(
            "Product ID is required for delivery item at index "
            f"{flow_index} (part_number='{part_number}')"
        )
