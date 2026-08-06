from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


class FluentDict[ItemT](dict[str, ItemT]):
    def value_of(self, key: str) -> FluentElement[ItemT]:
        return FluentElement(self[key])

    def and_a(self, **fields: ItemT) -> FluentDict[ItemT]:
        return self.with_a(**fields)

    def with_a(self, **fields: ItemT) -> FluentDict[ItemT]:
        return self.merge(FluentDict[ItemT](fields))

    def merge(self, other: FluentDict[ItemT]) -> FluentDict[ItemT]:
        return FluentDict[ItemT]({**self, **other})

    def drop(self, *keys: str) -> FluentDict[ItemT]:
        return self.select(*set(self.keys()).difference(keys))

    def select(self, *keys: str) -> FluentDict[ItemT]:
        return FluentDict[ItemT]({k: v for k, v in self.items() if k in keys})


@dataclass(frozen=True)
class FluentElement[ItemT]:
    value: ItemT

    def to[ConvertedT](self, a_type: Callable[[ItemT], ConvertedT]) -> ConvertedT:
        return a_type(self.value)

    def __str__(self) -> str:  # pragma: no cover
        return str(self.value)


JsonDict = FluentDict[Any]
