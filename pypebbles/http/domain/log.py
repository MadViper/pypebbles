from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Protocol

from pypebbles import JsonDict

if TYPE_CHECKING:
    from collections.abc import Callable

    from .method import HttpMethod
    from .request import HttpRequest
    from .response import HttpResponse


@dataclass(frozen=True)
class AccessLog:
    device: _Device = field(default_factory=lambda: EchoDevice(name="http.access"))

    def before(
        self,
        using: HttpMethod,
        request: HttpRequest,
    ) -> HttpRequest:
        log = HttpRequestLog(method=using, request=request)

        self.device.echo_request(log)

        return request.with_header(key="X-Trace-Id", value=log.trace_id)

    def after(
        self,
        using: HttpMethod,
        request: HttpRequest,
        response: HttpResponse,
    ) -> HttpResponse:
        log = HttpResponseLog(
            trace_id=request.headers.get("X-Trace-Id", "unknown"),
            method=using,
            response=response,
        )

        self.device.echo_response(log)

        return response


class _Device(Protocol):
    def echo_request(self, log: HttpRequestLog) -> None:
        pass

    def echo_response(self, log: HttpResponseLog) -> None:
        pass


@dataclass(frozen=True)
class EchoDevice:
    name: str

    echo: Callable[[str], Any] = print

    def echo_request(self, log: HttpRequestLog) -> None:
        self.echo(f"[{self.name}] Request:")
        self.echo(log.dumps())

    def echo_response(self, log: HttpResponseLog) -> None:
        self.echo(f"[{self.name}] Response:")
        self.echo(log.dumps())


@dataclass(frozen=True, kw_only=True)
class HttpLog:
    method: HttpMethod

    timestamp: int = field(default_factory=lambda: int(time.time()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()).split("-")[-1])

    def dumps(self) -> str:
        return json.dumps(self.dump(), indent=4)

    def dump(self) -> JsonDict:
        return (
            JsonDict()
            .with_a(trace_id=self.trace_id)
            .and_a(timestamp=self.timestamp)
            .and_a(method=self.method.name.upper())
        )


@dataclass(frozen=True)
class HttpRequestLog(HttpLog):
    request: HttpRequest

    def dump(self) -> JsonDict:
        return (
            super()
            .dump()
            .with_a(endpoint=self.request.endpoint)
            .and_a(json=self.request.json)
            .and_a(form=self.request.data)
            .and_a(params=self.request.params)
        )


@dataclass(frozen=True)
class HttpResponseLog(HttpLog):
    response: HttpResponse

    @property
    def body(self) -> bytes | JsonDict:
        try:
            return self.response.json()
        except JSONDecodeError:
            return self.response.content

    def dump(self) -> JsonDict:
        return super().dump().with_a(status=self.response.status).and_a(body=self.body)
