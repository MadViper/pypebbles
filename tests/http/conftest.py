from pathlib import Path

import pytest

from pypebbles import FluentDict
from pypebbles.http import HttpTransport
from pypebbles.http.drivers import Httpx
from pypebbles.http.fake import InternalEcho
from pypebbles.runtime import Environment


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
def echo(request: pytest.FixtureRequest, echo_host: str) -> HttpTransport:
    match request.param:
        case "external":
            return (
                Httpx.Builder()
                .with_base(url=echo_host)
                .with_header("User-Agent", "hogwarts")
                .build()
            )
        case "internal":
            return InternalEcho(
                server=echo_host,
                headers=FluentDict[str]({"User-Agent": "hogwarts"}),
            )
        case _ as kind:
            raise RuntimeError(f"Unknown kind: {kind}")
