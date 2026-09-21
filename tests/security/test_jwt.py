from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import pytest
from faker.proxy import Faker

from pypebbles.security import JWT


def test_token_is_the_same_for_the_same_key(fake: _Fake) -> None:
    key = _Fake().key()
    payload = fake.payload()

    assert JWT(key)(payload) == JWT(key)(payload)


def test_token_is_different_for_different_keys(fake: _Fake) -> None:
    key_1 = fake.key()
    key_2 = fake.key()
    payload = fake.payload()

    assert JWT(key_1)(payload) != JWT(key_2)(payload)


def test_roundtrip(fake: _Fake) -> None:
    key = fake.key()
    payload = fake.payload()

    assert JWT(key).decode(JWT(key).encode(payload)) == payload


@pytest.fixture
def fake() -> _Fake:
    return _Fake()


@dataclass(frozen=True)
class _Fake:
    faker: Faker = field(default_factory=Faker)

    def key(self) -> bytes:
        return self.faker.binary(length=32)

    def payload(self) -> Mapping[str, str | int | float]:
        return self.faker.pydict(value_types=[str, int, float])
