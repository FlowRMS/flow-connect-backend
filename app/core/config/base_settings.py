import functools
from typing import TypeVar

import dotenv
from pydantic_settings import BaseSettings

TSettings = TypeVar("TSettings", bound=BaseSettings)


@functools.cache
def load_dotenv_once(dotenv_path: str | None = None) -> None:
    _ = dotenv.load_dotenv(dotenv_path or ".env.dev")


def get_settings(cls: type[TSettings]) -> TSettings:
    load_dotenv_once()
    return cls()

def get_settings_local(env: str, cls: type[TSettings]) -> TSettings:
    _ = dotenv.load_dotenv(f".env.{env}")
    return cls()