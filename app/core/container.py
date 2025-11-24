import functools

import aioinject

from app.core.providers import providers


@functools.cache
def create_container() -> aioinject.Container:
    container = aioinject.Container()
    for provider in providers():
        container.register(provider)
    return container
