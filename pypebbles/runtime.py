from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol


class Provider(Protocol):
    def required_value_of(self, variable: str) -> str:
        pass

    def optional_value_of(self, variable: str, default: str) -> str:
        pass


@dataclass(frozen=True)
class _DefaultProvider(Provider):
    def required_value_of(self, variable: str) -> str:
        return os.environ[variable]

    def optional_value_of(self, variable: str, default: str) -> str:
        return os.getenv(variable, default)


@dataclass(frozen=True)
class Environment:
    provider: Provider = field(default_factory=_DefaultProvider)

    def inject(self, variable: str, *, default: str | None = None) -> str:
        return field(
            default_factory=lambda: self.value_of(
                variable=variable,
                default=default,
            )
        )

    def value_of(self, variable: str, *, default: str | None = None) -> str:
        if default is None:
            return self.provider.required_value_of(variable)

        return self.provider.optional_value_of(variable, default)
