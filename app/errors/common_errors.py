from app.errors.base_exception import BaseException


class NameAlreadyExistsError(BaseException):
    def __init__(self, name: str) -> None:
        super().__init__(f"An entity with the name '{name}' already exists")


class NotFoundError(BaseException):
    def __init__(self, entity_id: str) -> None:
        super().__init__(f"Entity with ID '{entity_id}' not found")


class ConflictError(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ValidationError(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnauthorizedError(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DeletionError(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TenantNotFoundError(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RemoteApiError(BaseException):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)
