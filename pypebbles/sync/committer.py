from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from .observers import CommitObserver


@dataclass(frozen=True)
class Committer[T]:
    commit_fn: Callable[[Iterable[T]], None]

    observers: list[CommitObserver] = field(default_factory=list)

    dry_run: bool = False

    @classmethod
    def using(cls, commit_fn: Callable[[Iterable[T]], None]) -> Committer[T]:
        return cls(commit_fn)

    def dry(self, *, when: bool) -> Committer[T]:
        return replace(self, dry_run=when)

    def attach(self, observer: CommitObserver) -> Self:
        self.observers.append(observer)

        return self

    def commit(self, items: Iterable[T]) -> None:
        self.notify_on_start()
        to_commit = list(items)

        self.notify_before_commit(len(to_commit))

        if not to_commit or self.dry_run:
            return

        try:
            self.commit_fn(to_commit)
        except Exception as e:
            self.notify_on_error(e)
            return

        self.notify_on_finish()

    def notify_on_start(self) -> None:
        for observer in self.observers:
            observer.on_start()

    def notify_on_finish(self) -> None:
        for observer in self.observers:
            observer.on_finish()

    def notify_on_error(self, error: Exception) -> None:
        for observer in self.observers:
            observer.on_error(error)

    def notify_before_commit(self, n_items: int) -> None:
        for observer in self.observers:
            observer.before_commit(n_items)
