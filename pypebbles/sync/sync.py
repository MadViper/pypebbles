from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from .observers import CommitObserver, ErrorCollector

if TYPE_CHECKING:
    from .stage import SyncStage


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
