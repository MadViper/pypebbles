import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass

import bcrypt


class Hasher(ABC):
    def __call__(self, value: str) -> bytes:
        return self.hash(value)

    @abstractmethod
    def hash(self, value: str) -> bytes:
        pass

    def verify(self, value: str, hashed: bytes) -> bool:
        return self.hash(value) == hashed


@dataclass(frozen=True)
class Hmac(Hasher):
    secret: str

    algorithm: str = "sha256"

    def hash(self, value: str) -> bytes:
        return hmac.new(
            key=self.secret.encode("utf-8"),
            msg=value.encode("utf-8"),
            digestmod=self.algorithm,
        ).digest()


@dataclass(frozen=True)
class Bcrypt(Hasher):
    def hash(self, value: str) -> bytes:
        return bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt())

    def verify(self, value: str, hashed: bytes) -> bool:
        return bcrypt.checkpw(value.encode("utf-8"), hashed)
