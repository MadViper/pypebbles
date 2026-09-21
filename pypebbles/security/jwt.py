from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import jwt

from pypebbles import JsonDict


@dataclass(frozen=True)
class JWT:
    secret: str

    algorithm: str = "HS256"

    def __call__(self, payload: Mapping[str, Any]) -> str:
        return self.encode(payload)

    def encode(self, payload: Mapping[str, Any]) -> str:
        return jwt.encode(
            payload=dict(payload),
            key=self.secret,
            algorithm=self.algorithm,
        )

    def decode(self, token: str) -> JsonDict:
        try:
            return JsonDict(self._decode(token))
        except jwt.exceptions.InvalidTokenError as e:
            raise ValueError("Invalid JWT token: {e}") from e

    def _decode(self, token: str) -> Mapping[str, Any]:
        return jwt.decode(
            jwt=token,
            key=self.secret,
            algorithms=[self.algorithm],
        )
