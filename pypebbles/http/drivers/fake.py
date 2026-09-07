from dataclasses import dataclass, field

from pypebbles import FluentDict
from pypebbles.http.domain import HttpMethod, HttpRequest, HttpResponse
from pypebbles.http.url import HttpUrl


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
