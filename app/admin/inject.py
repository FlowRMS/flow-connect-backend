import functools

import aioinject
from aioinject.ext.strawberry import inject as base_inject

from app.admin.context import AdminContext


def admin_context_getter(
    context: AdminContext,
) -> aioinject.Context | aioinject.SyncContext:
    return context.aioinject_context  # type: ignore[return-value]


def admin_context_setter(
    context: AdminContext,
    aioinject_context: aioinject.Context | aioinject.SyncContext,
) -> None:
    context.aioinject_context = aioinject_context  # type: ignore[attr-defined]


admin_inject = functools.partial(base_inject, context_getter=admin_context_getter)

__all__ = ["admin_inject", "admin_context_setter", "admin_context_getter"]
