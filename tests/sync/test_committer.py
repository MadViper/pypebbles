from collections.abc import Iterable
from unittest.mock import MagicMock

import pytest
from faker import Faker

from pypebbles.sync import Committer, ErrorCollector

ItemType = int | str


@pytest.fixture
def selection(faker: Faker) -> Iterable[ItemType]:
    return faker.pylist(
        nb_elements=10,
        variable_nb_elements=True,
        value_types=[int, str],
    )


def test_should_not_commit_when_empty() -> None:
    target = MagicMock()

    Committer.using(target).commit([])

    target.assert_not_called()


def test_should_not_commit_when_dry(selection: Iterable[ItemType]) -> None:
    target = MagicMock()

    Committer.using(target).dry(when=True).commit(selection)

    target.assert_not_called()


def test_should_commit(selection: Iterable[ItemType]) -> None:
    target = MagicMock()

    Committer.using(target).commit(selection)

    target.assert_called_once_with(selection)


def test_should_not_notify_error(selection: Iterable[ItemType]) -> None:
    observer = ErrorCollector()

    Committer.using(MagicMock()).attach(observer).commit(selection)

    observer.fire()


def test_should_notify_error(selection: Iterable[ItemType]) -> None:
    target = MagicMock(side_effect=RuntimeError("Cannot commit"))
    observer = ErrorCollector()

    Committer.using(target).attach(observer).commit(selection)

    with pytest.raises(ExceptionGroup, match="Sync Failed!"):
        observer.fire()


def test_should_notify_before_commit(selection: Iterable[ItemType]) -> None:
    observer = MagicMock()

    Committer.using(MagicMock()).attach(observer).commit(selection)

    observer.before_commit.assert_called_once_with(len(list(selection)))


def test_should_notify_after_commit(selection: Iterable[ItemType]) -> None:
    observer = MagicMock()

    Committer.using(MagicMock()).attach(observer).commit(selection)

    observer.on_finish.assert_called_once_with()
