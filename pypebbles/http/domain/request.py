from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Protocol
from urllib.parse import urlencode

from pypebbles import FluentDict, JsonDict

from .method import HttpMethod
from .url import HttpUrl


@dataclass(frozen=True)
class HttpRequest:
    endpoint: str = ""
    headers: FluentDict[str] = field(default_factory=FluentDict[str])
    params: FluentDict[str] = field(default_factory=FluentDict[str])
    json: JsonDict | None = None
    data: JsonDict | None = None

    @property
    def query(self) -> str:
        return f"{self.endpoint}?{urlencode(self.params)}".strip("?")

    def with_endpoint(self, endpoint: str) -> HttpRequest:
        return replace(self, endpoint=HttpUrl(self.endpoint) + endpoint)

    def with_header(self, key: str, value: str) -> HttpRequest:
        return self.with_headers({key: value})

    def with_headers(self, value: Mapping[str, str]) -> HttpRequest:
        return replace(self, headers=self.headers.merge(value))

    def with_param(self, key: str, value: str) -> HttpRequest:
        return self.with_params({key: value})

    def with_params(self, value: Mapping[str, str]) -> HttpRequest:
        return replace(self, params=self.params.merge(value))

    def with_data(self, value: JsonDict) -> HttpRequest:
        return replace(
            self,
            data=value,
            headers=self.headers.merge(
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            ),
        )

    def with_json(self, value: JsonDict) -> HttpRequest:
        return replace(
            self,
            json=value,
            headers=self.headers.merge(
                {
                    "Content-Type": "application/json",
                }
            ),
        )

    def using[T](self, transport: HttpTransport[T]) -> HttpDispatcher[T]:
        return HttpDispatcher(request=self, transport=transport)


@dataclass(frozen=True)
class HttpDispatcher[T]:
    request: HttpRequest
    transport: HttpTransport[T]

    def post(self) -> T:
        return self.dispatch(HttpMethod.post)

    def get(self) -> T:
        return self.dispatch(HttpMethod.get)

    def patch(self) -> T:
        return self.dispatch(HttpMethod.patch)

    def delete(self) -> T:
        return self.dispatch(HttpMethod.delete)

    def put(self) -> T:
        return self.dispatch(HttpMethod.put)

    def dispatch(self, method: HttpMethod) -> T:
        return self.transport.deliver(self.request, using=method)


class HttpTransport[T](Protocol):
    def deliver(self, request: HttpRequest, using: HttpMethod) -> T:
        pass
