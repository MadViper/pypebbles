from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class Selector[T](ABC):  # pragma: no cover
    def __call__(self, items: Iterable[T]) -> Iterable[T]:
        return self.select(items)

    @abstractmethod
    def select(self, items: Iterable[T]) -> Iterable[T]:
        pass

    def only_changes(self, *, when: bool = True) -> Selector[T]:
        return ChangeSelector(self) if when else self


@dataclass(frozen=True)
class AllSelector[T](Selector[T]):
    def select(self, items: Iterable[T]) -> Iterable[T]:
        return items


@dataclass(frozen=True)
class ChangeSelector[T](Selector[T]):
    inner: Selector[T]

    def select(self, items: Iterable[T]) -> Iterable[T]:
        target = set(items)

        return set(self.inner.select(target)).difference(target)
