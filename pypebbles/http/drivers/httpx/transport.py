from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from httpx2 import Client, Response

from pypebbles.http.domain import (
    HttpMethod,
    HttpRequest,
    HttpResponse,
    HttpTransportBuilder,
)

from .hooks import (
    AfterResponseHook,
    BeforeRequestHook,
    RequestHandler,
    ResponseHandler,
    SignPayloadWith,
)

if TYPE_CHECKING:
    from pypebbles.http import HttpTransport
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

    @dataclass(frozen=True)
    class Builder(HttpTransportBuilder):
        request_handlers: list[RequestHandler] = field(default_factory=list)
        response_handlers: list[ResponseHandler] = field(default_factory=list)

        def sign_payload_with(self, authority: Authority) -> Self:
            self.request_handlers.append(SignPayloadWith(authority))

            return self

        def before_request(self, handler: RequestHandler) -> Self:
            self.request_handlers.append(handler)

            return self

        def after_response(self, handler: ResponseHandler) -> Self:
            self.response_handlers.append(handler)

            return self

        def transport(self) -> HttpTransport[HttpResponse]:
            return Httpx(client=self.client())

        def client(self) -> Client:
            return Client(
                base_url=self.url,
                timeout=self.timeout_s,
                headers=self.headers,
                event_hooks={
                    "request": [
                        BeforeRequestHook(handler) for handler in self.request_handlers
                    ],
                    "response": [
                        AfterResponseHook(handler) for handler in self.response_handlers
                    ],
                },
            )
