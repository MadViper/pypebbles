from pathlib import Path

import pytest

from pypebbles import FluentDict
from pypebbles.http import HttpTransport
from pypebbles.http.fake import InternalEcho
from pypebbles.http.httpx import HttpxBuilder
from pypebbles.runtime import Environment


@pytest.fixture(scope="module")
def vcr_cassette_dir(request: pytest.FixtureRequest) -> str:
    module_path = Path(request.module.__file__)
    module_name = module_path.stem.removeprefix("test_")

    return str(module_path.parent / "cassettes" / module_name)


@pytest.fixture
def default_cassette_name(request: pytest.FixtureRequest) -> str:
    return str(request.node.name).removeprefix("test_").removeprefix("should_")


@pytest.fixture(params=["internal", "external"])
def transport(request: pytest.FixtureRequest) -> HttpTransport:
    match request.param:
        case "external":
            return (
                HttpxBuilder()
                .with_url(
                    Environment().value_of(
                        "ECHO_SERVER",
                        default="http://localhost:8080",
                    )
                )
                .with_header("User-Agent", "hogwarts")
                .transport()
            )
        case "internal":
            return InternalEcho(headers=FluentDict[str]({"User-Agent": "hogwarts"}))
        case _ as kind:
            raise RuntimeError(f"Unknown kind: {kind}")
