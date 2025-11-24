from contextvars import ContextVar, Token

from app.core.context import Context


class ContextWrapper:
    def __init__(self) -> None:
        super().__init__()
        self._context: ContextVar[Context] = ContextVar("context", default=Context())

    def get(self) -> Context:
        return self._context.get()

    def set(self, value: Context) -> Token[Context]:
        return self._context.set(value)

    def reset(self, token: Token[Context]) -> None:
        self._context.reset(token)


def create_context_wrapper() -> ContextWrapper:
    return ContextWrapper()
