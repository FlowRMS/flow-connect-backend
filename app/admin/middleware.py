from collections.abc import AsyncGenerator
from contextvars import ContextVar, Token
from typing import override

from loguru import logger
from strawberry.extensions import SchemaExtension

from app.admin.config.admin_settings import AdminSettings
from app.admin.context import AdminContext
from app.auth.workos_auth_service import WorkOSAuthService
from app.core.container import create_container

admin_context_var: ContextVar[AdminContext | None] = ContextVar(
    "admin_context", default=None
)


class AdminContextWrapper:
    def __init__(self) -> None:
        super().__init__()
        self._context_var = admin_context_var

    def get(self) -> AdminContext | None:
        return self._context_var.get()

    def set(self, context: AdminContext) -> Token[AdminContext | None]:
        return self._context_var.set(context)

    def reset(self, token: Token[AdminContext | None]) -> None:
        self._context_var.reset(token)


class AdminGraphQLMiddleware(SchemaExtension):
    @override
    async def on_execute(self) -> AsyncGenerator[None, None]:
        ctx = self.execution_context
        logger.info(f"[Admin API] [{ctx.query}] vars='{ctx.variables}'")
        yield

    @override
    async def on_operation(self) -> AsyncGenerator[None, None]:
        context: AdminContext = self.execution_context.context

        if context.request is None:
            logger.error("Request is None in admin middleware")
            yield
            return

        async with create_container().context() as conn_ctx:
            workos_service = await conn_ctx.resolve(WorkOSAuthService)
            admin_settings = await conn_ctx.resolve(AdminSettings)

            async with AdminContext.set_context(
                request=context.request,  # pyright: ignore[reportArgumentType]
                workos_service=workos_service,
                admin_settings=admin_settings,
            ) as context_model:
                context.initialize(context_model)
                wrapper = AdminContextWrapper()
                wrapper_token = wrapper.set(context)
                yield
                wrapper.reset(wrapper_token)
