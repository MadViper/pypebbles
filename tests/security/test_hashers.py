import pytest

from pypebbles.security import Bcrypt, Hasher, Hmac, NoHash

from .conftest import _Fake


def test(hasher: Hasher, fake: _Fake) -> None:
    message = fake.message()

    assert hasher.verify(message, hashed=hasher.hash(message))
    assert not hasher.verify(message[1:], hashed=hasher.hash(message))


@pytest.fixture(params=["none", "hmac", "bcrypt"])
def hasher(request: pytest.FixtureRequest, fake: _Fake) -> Hasher:
    match request.param:
        case "none":
            return NoHash()
        case "hmac":
            return Hmac(fake.key())
        case "bcrypt":
            return Bcrypt()
        case _:  # pragma: no cover
            raise RuntimeError(f"Unknown hasher: {request.param}")
