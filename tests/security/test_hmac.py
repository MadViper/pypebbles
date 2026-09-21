from pypebbles.security import Hmac

from .conftest import _Fake


def test(fake: _Fake) -> None:
    key = fake.key()
    message = fake.message()

    assert Hmac(key).verify(message, hashed=Hmac(key).hash(message))
    assert not Hmac(key).verify(message[1:], hashed=Hmac(key).hash(message))


def test_should_give_the_same_hash_for_same_keys(fake: _Fake) -> None:
    key = fake.key()
    message = fake.message()

    assert Hmac(key).hash(message) == Hmac(key).hash(message)


def test_should_give_different_hash_for_different_keys(fake: _Fake) -> None:
    key_1 = fake.key()
    key_2 = fake.key()
    message = fake.message()

    assert Hmac(key_1).hash(message) != Hmac(key_2).hash(message)
