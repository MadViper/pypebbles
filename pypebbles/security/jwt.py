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
        return JsonDict(
            jwt.decode(
                jwt=token,
                key=self.secret,
                algorithms=[self.algorithm],
            )
        )
