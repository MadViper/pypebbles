from pypebbles.security import JWT

from .conftest import _Fake


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
