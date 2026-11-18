from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from .committer import Committer
from .selectors import AllSelector, Selector

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from .observers import CommitObserver


@dataclass(frozen=True)
class SyncStage[T]:
    committer: Committer[T]
    selector: Selector[T]

    items: Iterable[T] = field(default_factory=list)

    @classmethod
    def using(cls, commit_fn: Callable[[Iterable[T]], None]) -> SyncStage[T]:
        return cls(Committer.using(commit_fn), AllSelector())

    def with_selector(self, value: Selector[T]) -> SyncStage[T]:
        return replace(self, selector=value)

    def attach(self, observer: CommitObserver) -> SyncStage[T]:
        return replace(self, committer=self.committer.attach(observer))

    def stage(self, items: Iterable[T]) -> SyncStage[T]:
        return replace(self, items=items)

    def only_changes(self, *, when: bool = False) -> SyncStage[T]:
        return replace(self, selector=self.selector.only_changes(when=when))

    def dry(self, *, when: bool = False) -> SyncStage[T]:
        return replace(self, committer=self.committer.dry(when=when))

    def commit(self) -> SyncStage[T]:
        def selected() -> Iterable[T]:
            yield from self.selector.select(self.items)

        self.committer.commit(selected())

        return self
