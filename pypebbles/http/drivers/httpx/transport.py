from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from httpx2 import Client, Response

from pypebbles import FluentDict
from pypebbles.http.domain import (
    Hooked,
    HttpHook,
    HttpMethod,
    HttpRequest,
    HttpResponse,
)

from .hooks import (
    AfterResponseHook,
    BeforeRequestHook,
    RequestHandler,
    ResponseHandler,
    SignPayloadWith,
)

if TYPE_CHECKING:
    from pypebbles.http.domain import HttpTransport
    from pypebbles.security import Authority


@dataclass(frozen=True)
class Httpx:
    client: Client

    def deliver(self, request: HttpRequest, using: HttpMethod) -> HttpResponse:
        return self.parse(
            self.client.request(
                method=using.name,
                url=request.endpoint,
                headers=request.headers,
                params=request.params,
                json=request.json,
                data=request.data,
            )
        )

    @staticmethod
    def parse(response: Response) -> HttpResponse:
        return HttpResponse(
            status=response.status_code,
            content=response.content,
        )

    def hook(self, with_a: HttpHook[HttpResponse]) -> HttpTransport[HttpResponse]:
        return Hooked(self, hook=with_a)

    @dataclass(frozen=True)
    class Builder:
        url: str = ""
        timeout_s: int = 30

        headers: FluentDict[str] = field(default_factory=FluentDict[str])

        request_handlers: list[RequestHandler] = field(default_factory=list)
        response_handlers: list[ResponseHandler] = field(default_factory=list)

        def with_base(self, *, url: str) -> Httpx.Builder:
            return replace(self, url=url)

        def with_header(self, key: str, value: str) -> Httpx.Builder:
            return replace(self, headers=self.headers.merge({key: value}))

        def with_timeout(self, *, seconds: int) -> Httpx.Builder:
            return replace(self, timeout_s=seconds)

        def sign_payload_with(self, authority: Authority) -> Httpx.Builder:
            self.request_handlers.append(SignPayloadWith(authority))

            return self

        def before_request(self, handler: RequestHandler) -> Httpx.Builder:
            self.request_handlers.append(handler)

            return self

        def after_response(self, handler: ResponseHandler) -> Httpx.Builder:
            self.response_handlers.append(handler)

            return self

        def build(self) -> Httpx:
            return Httpx(
                client=Client(
                    base_url=self.url,
                    timeout=self.timeout_s,
                    headers=self.headers,
                    event_hooks={
                        "request": [
                            BeforeRequestHook(handler)
                            for handler in self.request_handlers
                        ],
                        "response": [
                            AfterResponseHook(handler)
                            for handler in self.response_handlers
                        ],
                    },
                )
            )
