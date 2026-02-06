from dataclasses import dataclass


@dataclass(frozen=True)
class PreferenceKeyConfig:
    allowed_values: list[str] | None = None
