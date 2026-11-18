from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Protocol, Self

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


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


class CommitObserver:  # pragma: no
    def on_start(self) -> None:
        pass

    def on_finish(self) -> None:
        pass

    def on_error(self, error: Exception) -> None:
        pass

    def before_commit(self, n_items: int) -> None:
        pass


@dataclass(frozen=True)
class ErrorCollector(CommitObserver):
    errors: list[Exception] = field(default_factory=list)

    def on_error(self, error: Exception) -> None:
        self.errors.append(error)

    def fire(self) -> None:
        if not self.errors:
            return

        raise ExceptionGroup("Sync Failed!", self.errors)


@dataclass(frozen=True)
class CommitLog(CommitObserver):  # pragma: no cover
    operation: str
    clock: Clock

    echo: Callable[[str], None] = print

    class Clock(Protocol):
        def utcnow(self) -> str:
            pass

    @property
    def title(self) -> str:
        return self.operation.title()

    def on_start(self) -> None:
        self.echo(f">>> {self.title}")
        self.echo("---")
        self.echo(f"\tStart At: {self.clock.utcnow()}")

    def on_finish(self) -> None:
        self.echo(f"\tFinish At: {self.clock.utcnow()}")
        self.echo("\n")

    def on_error(self, error: Exception) -> None:
        _ = error

        self.echo(f"--- {self.title} Error ---")

    def before_commit(self, n_items: int) -> None:
        self.echo(f"\t# of items to commit: {n_items}")


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


@dataclass(frozen=True)
class Sync[T]:
    stages: list[SyncStage[T]] = field(default_factory=list)
    collector: ErrorCollector = field(default_factory=ErrorCollector)

    def add(self, stage: SyncStage[T]) -> Sync[T]:
        self.stages.append(stage)

        return self

    def attach(self, observer: CommitObserver) -> Sync[T]:
        return replace(self, stages=[stage.attach(observer) for stage in self.stages])

    def only_changes(self, *, when: bool = False) -> Sync[T]:
        return replace(
            self,
            stages=[stage.only_changes(when=when) for stage in self.stages],
        )

    def dry(self, *, when: bool = False) -> Sync[T]:
        return replace(
            self,
            stages=[stage.dry(when=when) for stage in self.stages],
        )

    def commit(self) -> Sync[T]:
        for stage in self.stages:
            stage.attach(self.collector).commit()

        return self

    def if_error(self) -> ErrorCollector:
        return self.collector
