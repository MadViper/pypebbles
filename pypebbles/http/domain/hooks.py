from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Protocol

from .method import HttpMethod
from .request import HttpRequest, HttpTransport


@dataclass(frozen=True)
class Hooked[T]:
    transport: HttpTransport[T]

    hook: HttpHook[T] = field(default_factory=lambda: NoHook())

    def attach(self, hook: HttpHook[T]) -> Hooked[T]:
        return replace(self, hook=hook)

    def deliver(self, request: HttpRequest, using: HttpMethod) -> T:
        request = self.hook.before(using, request)
        response = self.transport.deliver(request, using)

        return self.hook.after(using, request, response)


class HttpHook[T](Protocol):  # pragma: no cover
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
        response: T,
    ) -> T:
        pass


@dataclass(frozen=True)
class NoHook[T]:
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
        response: T,
    ) -> T:
        _ = using, request

        return response
