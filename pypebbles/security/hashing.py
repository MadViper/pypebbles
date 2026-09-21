import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Hasher(ABC):
    def __call__(self, value: str) -> bytes:
        return self.hash(value)

    @abstractmethod
    def hash(self, value: str) -> bytes:
        pass


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
