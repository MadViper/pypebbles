from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from pypebbles import FluentDict
from pypebbles.security import Hash

from .hooks import Hooked, HttpHook
from .log import AccessLog, EchoDevice

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Self

    from .request import HttpTransport
    from .response import HttpResponse


@dataclass(frozen=True)
class HttpTransportBuilder(ABC):
    url: str = ""
    timeout_s: int = 30
    headers: FluentDict[str] = field(default_factory=FluentDict[str])
    hooks: list[HttpHook[HttpResponse]] = field(default_factory=list)

    def with_base(self, *, url: str) -> Self:
        return replace(self, url=url)

    def with_basic_auth(self, username: str, password: str) -> Self:
        credentials = Hash.from_text(f"{username}:{password}").b64()

        return self.with_header(key="Authorization", value=f"Basic {credentials}")

    def with_user_agent(self, named: str) -> Self:
        return self.with_header(key="User-Agent", value=named)

    def with_header(self, key: str, value: str) -> Self:
        return replace(self, headers=self.headers.merge({key: value}))

    def with_timeout(self, *, seconds: int) -> Self:
        return replace(self, timeout_s=seconds)

    def log(self, name: str, echo: Callable[[str], Any] = print) -> Self:
        return self.hook(with_a=AccessLog(device=EchoDevice(name=name, echo=echo)))

    def hook(self, with_a: HttpHook[HttpResponse]) -> Self:
        self.hooks.append(with_a)

        return self

    def build(self) -> HttpTransport[HttpResponse]:
        return self.hooked(self.transport())

    def hooked(self, http: HttpTransport[HttpResponse]) -> HttpTransport[HttpResponse]:
        transport: HttpTransport[HttpResponse] = http

        for hook in self.hooks:
            transport = Hooked(transport, hook=hook)

        return transport

    @abstractmethod
    def transport(self) -> HttpTransport[HttpResponse]:
        pass
