from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Protocol

from .method import HttpMethod
from .request import HttpRequest, HttpTransport
from .response import HttpResponse


@dataclass(frozen=True)
class Hooked:
    transport: HttpTransport

    hook: HttpHook = field(default_factory=lambda: NoHook())

    def attach(self, hook: HttpHook) -> Hooked:
        return replace(self, hook=hook)

    def deliver(self, request: HttpRequest, using: HttpMethod) -> HttpResponse:
        request = self.hook.before(using, request)
        response = self.transport.deliver(request, using)

        return self.hook.after(using, request, response)


class HttpHook(Protocol):  # pragma: no cover
    def before(
        self,
        using: HttpMethod,
        request: HttpRequest,
    ) -> HttpRequest:
        pass

    def after(
        self,
        using: HttpMethod,
        request: HttpRequest,
        response: HttpResponse,
    ) -> HttpResponse:
        pass


@dataclass(frozen=True)
class NoHook:
    def before(
        self,
        using: HttpMethod,
        request: HttpRequest,
    ) -> HttpRequest:
        _ = using

        return request

    def after(
        self,
        using: HttpMethod,
        request: HttpRequest,
        response: HttpResponse,
    ) -> HttpResponse:
        _ = using, request

        return response
