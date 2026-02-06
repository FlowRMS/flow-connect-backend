from app.errors.base_exception import BaseException


class UserNotFoundError(BaseException):
    def __init__(self, workos_user_id: str) -> None:
        self.workos_user_id = workos_user_id
        super().__init__(f"User with WorkOS ID '{workos_user_id}' not found")


class UserOrganizationRequiredError(BaseException):
    def __init__(self, workos_user_id: str) -> None:
        self.workos_user_id = workos_user_id
        super().__init__(
            f"User with WorkOS ID '{workos_user_id}' has no primary organization"
        )
