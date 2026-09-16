from dataclasses import dataclass
from pathlib import Path

import pytest

from pypebbles.http import (
    HttpMethod,
    HttpRequest,
    HttpResponse,
    HttpTransport,
    Httpx,
    InternalEcho,
)
from pypebbles.runtime import Environment

from .echo import Echo


@pytest.fixture(scope="module")
def vcr_cassette_dir(request: pytest.FixtureRequest) -> str:
    module_path = Path(request.module.__file__)
    module_name = module_path.stem.removeprefix("test_")

    return str(module_path.parent / "cassettes" / module_name)


@pytest.fixture
def default_cassette_name(request: pytest.FixtureRequest) -> str:
    return str(request.node.name).removeprefix("test_").removeprefix("should_")


@pytest.fixture
def echo_host() -> str:
    return Environment().value_of("ECHO_SERVER", default="http://localhost:8080")


@pytest.fixture(params=["internal", "external"])
def echo(request: pytest.FixtureRequest, echo_host: str) -> HttpTransport[Echo]:
    builder: type[Httpx.Builder] | type[InternalEcho.Builder]

    match request.param:
        case "external":
            builder = Httpx.Builder
        case "internal":
            builder = InternalEcho.Builder
        case _ as kind:
            raise RuntimeError(f"Unknown kind: {kind}")

    return _EchoTransport(
        builder()
        .with_base(url=echo_host)
        .with_timeout(seconds=10)
        .with_header("User-Agent", "hogwarts")
        .build()
    )


@dataclass(frozen=True)
class _EchoTransport:
    transport: HttpTransport[HttpResponse]

    def deliver(self, request: HttpRequest, using: HttpMethod) -> Echo:
        return self.transport.deliver(request=request, using=using).load(Echo)
