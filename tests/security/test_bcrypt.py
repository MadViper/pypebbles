from pypebbles.security.hashing import Bcrypt

from .conftest import _Fake


def test(fake: _Fake) -> None:
    message = fake.message()

    assert Bcrypt().verify(message, hashed=Bcrypt().hash(message))
    assert not Bcrypt().verify(message[1:], hashed=Bcrypt().hash(message))
