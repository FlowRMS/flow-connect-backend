from strawberry.exceptions import StrawberryGraphQLError


class BaseException(StrawberryGraphQLError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            original_error=self,
            extensions={"exception": self.__class__.__name__},
        )
