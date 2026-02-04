import functools

import aioinject
from aioinject.ext.strawberry import inject as base_inject

from app.core.context import Context


def context_getter(
    context: Context,
) -> aioinject.Context | aioinject.SyncContext:
    """Custom context getter for aioinject that works with BaseContext subclasses."""
    return context.aioinject_context  # type: ignore[return-value]


def context_setter(
    context: Context,
    aioinject_context: aioinject.Context | aioinject.SyncContext,
) -> None:
    """Custom context setter for aioinject that works with BaseContext subclasses."""
    context.aioinject_context = aioinject_context  # type: ignore[attr-defined]


inject = functools.partial(base_inject, context_getter=context_getter)

__all__ = ["inject", "context_setter", "context_getter"]
