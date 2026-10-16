from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pypebbles import JsonDict


class Authority(Protocol):  # pragma: no cover
    def sign(self, message: str) -> Signature:
        pass

    def verify(self, message: str, signature: Signature) -> bool:
        pass


@dataclass(frozen=True, kw_only=True)
class Signature:
    name: str
    value: str


class Encoder(Protocol):  # pragma: no cover
    def __call__(self, payload: Mapping[str, Any]) -> str:
        pass

    def encode(self, payload: Mapping[str, Any]) -> str:
        pass

    def decode(self, token: str) -> JsonDict:
        pass
