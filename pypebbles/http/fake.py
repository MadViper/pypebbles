from dataclasses import dataclass, field

from pypebbles import FluentDict
from pypebbles.runtime import Environment

from .domain import HttpMethod, HttpRequest, HttpResponse
from .url import HttpUrl


@dataclass(frozen=True)
class InternalEcho:
    headers: FluentDict[str] = field(default_factory=FluentDict[str])

    server: str = Environment().inject(
        variable="ECHO_SERVER",
        default="http://localhost:8080",
    )

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
