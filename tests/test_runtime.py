import os
from collections.abc import Iterable
from dataclasses import dataclass

import pytest

from pypebbles.runtime import Environment


@pytest.fixture
def variable() -> Iterable[tuple[str, str]]:
    name, value = "Harry", "Potter"

    os.environ[name] = value

    yield name, value

    del os.environ[name]


def test_should_fail_to_fetch_unknown() -> None:
    with pytest.raises(KeyError):
        Environment().value_of(variable="unknown")


def test_should_fetch(variable: tuple[str, str]) -> None:
    name, value = variable

    assert Environment().value_of(variable=name) == value


def test_should_fetch_with_default() -> None:
    default = "known"

    assert Environment().value_of(variable="unknown", default=default) == default


def test_should_fail_to_fetch_unknown_as_dataclass_field() -> None:
    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable="unknown")

    with pytest.raises(KeyError):
        _TestSubject()


def test_should_fetch_as_dataclass_field(variable: tuple[str, str]) -> None:
    name, value = variable

    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable=name)

    assert _TestSubject().value == value


def test_should_fetch_as_dataclass_field_with_default() -> None:
    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable="unknown", default="known")

    assert _TestSubject().value == "known"
