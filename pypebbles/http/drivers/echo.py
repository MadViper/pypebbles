from __future__ import annotations

from dataclasses import dataclass, field, replace

from pypebbles import FluentDict
from pypebbles.http import HttpMethod, HttpRequest, HttpResponse, HttpTransport, HttpUrl


@dataclass(frozen=True)
class InternalEcho:
    server: str

    headers: FluentDict[str] = field(default_factory=FluentDict[str])

    def deliver(self, request: HttpRequest, using: HttpMethod) -> HttpResponse:
        if request.endpoint != using.name:  # pragma: no cover
            return HttpResponse(status=405).set_json({"method": request.endpoint})

        return HttpResponse(status=200).set_json(
            {
                "url": HttpUrl(self.server) + request.query,
                "headers": request.headers.merge(self.headers),
                "json": request.json,
                "form": request.data,
            }
        )

    @dataclass(frozen=True)
    class Builder:
        url: str = ""

        headers: FluentDict[str] = field(default_factory=FluentDict[str])

        def with_base(self, *, url: str) -> InternalEcho.Builder:
            return replace(self, url=url)

        def with_header(self, key: str, value: str) -> InternalEcho.Builder:
            return replace(self, headers=self.headers.merge({key: value}))

        def with_timeout(self, *, seconds: int) -> InternalEcho.Builder:
            _ = seconds

            return self

        def build(self) -> HttpTransport[HttpResponse]:
            return InternalEcho(server=self.url, headers=self.headers)
