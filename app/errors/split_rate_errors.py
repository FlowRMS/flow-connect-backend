from uuid import UUID

from app.errors.base_exception import BaseException


class DuplicateUserInSplitRatesError(BaseException):
    def __init__(self, user_ids: set[UUID]) -> None:
        ids_str = ", ".join(str(uid) for uid in user_ids)
        super().__init__(f"Duplicate user IDs in split rates: {ids_str}")


class UserNotFoundInSplitRateError(BaseException):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User with ID '{user_id}' not found")


class InvalidInsideRepError(BaseException):
    def __init__(self, first_name: str, last_name: str) -> None:
        super().__init__(
            f"User '{first_name} {last_name}' cannot be an inside rep "
            "(inside flag is not set)"
        )


class InvalidOutsideRepError(BaseException):
    def __init__(self, first_name: str, last_name: str) -> None:
        super().__init__(
            f"User '{first_name} {last_name}' cannot be an outside rep "
            "(outside flag is not set)"
        )


class InvalidFactoryRepError(BaseException):
    def __init__(self, first_name: str, last_name: str) -> None:
        super().__init__(
            f"User '{first_name} {last_name}' cannot be a factory rep "
            "(inside flag is not set)"
        )
