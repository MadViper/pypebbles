from __future__ import annotations

import base64
import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass

import bcrypt


class Hasher(ABC):
    def __call__(self, value: str) -> Hash:
        return self.hash(value)

    @abstractmethod
    def hash(self, value: str) -> Hash:
        pass

    def verify(self, value: str, hashed: Hash) -> bool:
        return self.hash(value) == hashed


@dataclass(frozen=True)
class Hash:
    raw: bytes

    @classmethod
    def from_text(cls, value: str) -> Hash:
        return cls(value.encode("utf-8"))

    def text(self) -> str:
        return self.raw.decode("utf-8")

    @classmethod
    def from_hex(cls, value: str) -> Hash:
        return cls(bytes.fromhex(value))

    def hex(self) -> str:
        return self.raw.hex()

    def b64(self) -> str:
        return base64.b64encode(self.raw).decode()

    @classmethod
    def from_b64(cls, value: str) -> Hash:
        return cls(base64.b64decode(value))


@dataclass(frozen=True)
class Hmac(Hasher):
    secret: str

    algorithm: str = "sha256"

    def hash(self, value: str) -> Hash:
        return Hash(
            hmac.new(
                key=self.secret.encode("utf-8"),
                msg=value.encode("utf-8"),
                digestmod=self.algorithm,
            ).digest()
        )


@dataclass(frozen=True)
class Bcrypt(Hasher):
    def hash(self, value: str) -> Hash:
        return Hash(bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt()))

    def verify(self, value: str, hashed: Hash) -> bool:
        return bcrypt.checkpw(value.encode("utf-8"), hashed.raw)
