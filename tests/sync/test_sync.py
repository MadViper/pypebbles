from unittest.mock import MagicMock

import pytest

from pypebbles.sync import Sync, SyncStage


def test_should_not_commit_when_no_items() -> None:
    # Given
    commit = MagicMock()

    # When
    Sync().add(SyncStage.using(commit).stage([])).commit()

    # Then
    commit.assert_not_called()


def test_should_not_commit_when_dry_run() -> None:
    # Given
    items = [1, 2, 3, "Apple", "Orange"]
    commit = MagicMock()

    # When
    (
        Sync()
        .add(SyncStage.using(commit).stage(items))
        .only_changes(when=False)
        .dry(when=True)
        .commit()
    )

    # Then
    commit.assert_not_called()


def test_should_not_commit_when_no_changes() -> None:
    # Given
    items = [1, 2, 3, "Apple", "Orange"]
    commit = MagicMock()

    # When
    Sync().add(SyncStage.using(commit).stage(items)).only_changes(when=True).commit()

    # Then
    commit.assert_not_called()


def test_should_commit() -> None:
    # Given
    items = [1, 2, 3, "Apple", "Orange"]
    commit = MagicMock()

    # When
    Sync().add(SyncStage.using(commit).stage(items)).commit()

    # Then
    commit.assert_called_once_with(items)


def test_should_capture_error() -> None:
    # Given
    items = [1, 2, 3, "Apple", "Orange"]
    commit = MagicMock(side_effect=Exception("Something went wrong"))

    # When
    sync = Sync[int | str]().add(SyncStage.using(commit).stage(items)).commit()

    # Then
    with pytest.raises(Exception, match="Sync Failed!"):
        sync.if_error().fire()
