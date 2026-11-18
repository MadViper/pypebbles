from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable


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
