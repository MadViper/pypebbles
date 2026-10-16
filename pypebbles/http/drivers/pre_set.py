from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from pypebbles.http import HttpMethod, HttpRequest, HttpResponse

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping


def default_response() -> HttpResponse:
    return HttpResponse(status=200, content=b"{}")


@dataclass
class PreSetHttp:
    allowed: Collection[HttpMethod] = field(default_factory=list)
    response: HttpResponse = field(default_factory=default_response)
    intercepted: HttpRequest = field(default_factory=HttpRequest)

    def respond(self, json: Mapping[str, str]) -> PreSetHttp:
        return replace(self, response=self.response.set_json(json))

    def allow(self, method: HttpMethod) -> PreSetHttp:
        return replace(self, allowed=[*self.allowed, method])

    def deliver(self, request: HttpRequest, using: HttpMethod) -> HttpResponse:
        assert using in self.allowed, f"Method {using} not allowed"

        self.intercepted = request

        return self.response
