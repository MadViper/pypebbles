import json
from dataclasses import dataclass

from pypebbles.security import Authority

from .domain import HttpMethod, HttpRequest
from .domain.hooks import NoHook


@dataclass(frozen=True)
class SignPayloadWith(NoHook):
    authority: Authority

    def before(self, using: HttpMethod, request: HttpRequest) -> HttpRequest:
        if request.json is None or using != HttpMethod.post:
            return request

        signature = self.authority.sign(json.dumps(request.json))

        return request.with_header(key=signature.name, value=signature.value)
