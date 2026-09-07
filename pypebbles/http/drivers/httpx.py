from __future__ import annotations

from dataclasses import dataclass, field, replace

from httpx2 import Client, Response

from pypebbles import FluentDict
from pypebbles.http.domain import HttpMethod, HttpRequest, HttpResponse


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
    class Builder:
        url: str = ""
        timeout_s: int = 30

        headers: FluentDict[str] = field(default_factory=FluentDict[str])

        def with_base(self, *, url: str) -> Httpx.Builder:
            return replace(self, url=url)

        def with_header(self, key: str, value: str) -> Httpx.Builder:
            return replace(self, headers=self.headers.merge({key: value}))

        def with_timeout(self, *, seconds: int) -> Httpx.Builder:
            return replace(self, timeout_s=seconds)

        def build(self) -> Httpx:
            return Httpx(
                client=Client(
                    base_url=self.url,
                    timeout=self.timeout_s,
                    headers=self.headers,
                )
            )
