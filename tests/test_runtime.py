import os
from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass

import pytest

from pypebbles.runtime import Environment


@pytest.fixture
def variable() -> Iterable[tuple[str, str]]:
    name, value = "Harry", "Potter"

    os.environ[name] = value

    try:
        yield name, value
    finally:
        with suppress(KeyError):
            del os.environ[name]


def test_should_fetch_existing(variable: tuple[str, str]) -> None:
    name, value = variable

    assert Environment().value_of(variable=name) == value


def test_should_not_fetch_missing(variable: tuple[str, str]) -> None:
    name, _ = variable

    del os.environ[name]

    with pytest.raises(KeyError):
        Environment().value_of(variable=name)


def test_should_fetch_with_default(variable: tuple[str, str]) -> None:
    name, default = variable

    del os.environ[name]

    assert Environment().value_of(variable=name, default=default) == default


def test_should_not_inject_missing(variable: tuple[str, str]) -> None:
    name, _ = variable

    del os.environ[name]

    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable=name)

    with pytest.raises(KeyError):
        _TestSubject()


def test_should_fetch_as_dataclass_field(variable: tuple[str, str]) -> None:
    name, value = variable

    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable=name)

    assert _TestSubject().value == value


def test_should_fetch_as_dataclass_field_with_default() -> None:
    name, default = "unknown", "known"

    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable=name, default=default)

    assert _TestSubject().value == default
