from collections.abc import AsyncGenerator
from typing import override

from commons.auth import AuthInfo, AuthService
from commons.db.controller import MultiTenantController
from commons.db.models.tenant import Tenant
from loguru import logger
from sqlalchemy import select
from starlette.websockets import WebSocket
from strawberry.extensions import SchemaExtension

from app.core.container import create_container
from app.core.context import Context
from app.core.context_wrapper import ContextWrapper


async def _resolve_tenant_url(
    controller: MultiTenantController, auth_info: AuthInfo
) -> None:
    """Resolve tenant URL from WorkOS org_id and update auth_info.tenant_name.

    WorkOS JWT sets tenant_name from org_name (e.g., "Flow"), but MultiTenantController
    stores engines keyed by tenant.url (e.g., "app"). This function looks up the correct
    URL using the org_id and updates tenant_name so database routing works correctly.
    """
    if not auth_info.tenant_id:
        logger.debug("No tenant_id in auth_info, skipping tenant resolution")
        return

    original_tenant_name = auth_info.tenant_name
    async with controller.base_scoped_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Tenant.url).where(Tenant.org_id == auth_info.tenant_id)
            )
            tenant_url = result.scalar_one_or_none()
            if tenant_url:
                auth_info.tenant_name = tenant_url
                logger.info(
                    f"Tenant resolved: {original_tenant_name} -> {tenant_url} "
                    f"(org_id={auth_info.tenant_id})"
                )
            else:
                logger.warning(
                    f"No tenant found for org_id={auth_info.tenant_id}, "
                    f"keeping tenant_name={original_tenant_name}"
                )


class GraphQLMiddleware(SchemaExtension):
    @override
    async def on_execute(self) -> AsyncGenerator[None, None]:
        ctx = self.execution_context
        logger.info(f"[{ctx.query}] vars='{ctx.variables}'")
        yield

    @override
    async def on_operation(self) -> AsyncGenerator[None, None]:
        """Handle operation lifecycle including authentication and session management."""
        context: Context = self.execution_context.context

        temp_request = context.request

        if isinstance(temp_request, WebSocket):
            temp_request = self.execution_context.context.connection_params_info

        if context.request is None:
            logger.error("Request is None")
            yield
            return

        async with create_container().context() as conn_ctx:
            async with Context.set_context(
                request=temp_request,  # pyright: ignore[reportArgumentType]
                auth_service=await conn_ctx.resolve(AuthService),
            ) as context_model:
                controller = await conn_ctx.resolve(MultiTenantController)
                await _resolve_tenant_url(controller, context_model.auth_info)
                context.initialize(context_model)
                context_wrapper = await conn_ctx.resolve(ContextWrapper)
                wrapper_token = context_wrapper.set(context)
                yield
                context_wrapper.reset(wrapper_token)
