import os
from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass
from typing import TypedDict

import pytest

from pypebbles.runtime import Environment


class _Variable(TypedDict):
    name: str
    value: str


@pytest.fixture
def variable() -> Iterable[_Variable]:
    name, value = "Harry", "Potter"

    os.environ[name] = value

    try:
        yield _Variable(name=name, value=value)
    finally:
        with suppress(KeyError):
            del os.environ[name]


def test_should_fetch_existing(variable: _Variable) -> None:
    name, value = variable["name"], variable["value"]

    assert Environment().value_of(variable=name) == value


def test_should_not_fetch_missing(variable: _Variable) -> None:
    name, _ = variable["name"], variable["value"]

    del os.environ[name]

    with pytest.raises(KeyError):
        Environment().value_of(variable=name)


def test_should_fetch_with_default(variable: _Variable) -> None:
    name, default = variable["name"], variable["value"]

    del os.environ[name]

    assert Environment().value_of(variable=name, default=default) == default


def test_should_inject_existing(variable: _Variable) -> None:
    name, value = variable["name"], variable["value"]

    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable=name)

    assert _TestSubject().value == value


def test_should_not_inject_missing(variable: _Variable) -> None:
    name, _ = variable["name"], variable["value"]

    del os.environ[name]

    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable=name)

    with pytest.raises(KeyError):
        _TestSubject()


def test_should_inject_default(variable: _Variable) -> None:
    name, default = variable["name"], variable["value"]

    del os.environ[name]

    @dataclass
    class _TestSubject:
        value: str = Environment().inject(variable=name, default=default)

    assert _TestSubject().value == default
