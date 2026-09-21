from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from faker import Faker

from pypebbles.security import Hmac


def test_hmac_is_the_same_for_the_same_key(fake: _Fake) -> None:
    key = fake.key()
    message = fake.message()

    assert Hmac(key)(message) == Hmac(key)(message)


def test_hmac_is_different_for_different_keys(fake: _Fake) -> None:
    key_1 = fake.key()
    key_2 = fake.key()
    message = fake.message()

    assert Hmac(key_1)(message) != Hmac(key_2)(message)


@pytest.fixture
def fake() -> _Fake:
    return _Fake()


@dataclass(frozen=True)
class _Fake:
    faker: Faker = field(default_factory=Faker)

    def key(self) -> str:
        return self.faker.word()

    def message(self) -> str:
        return self.faker.sentence()
