from dataclasses import dataclass

import pytest

from pypebbles.http import HttpMethod, HttpRequest, HttpTransport
from pypebbles.http.domain.hooks import Hooked, NoHook
from pypebbles.http.fake import InternalEcho
from pypebbles.http.httpx import HttpxBuilder
from pypebbles.runtime import Environment

from .echo import Echo


@pytest.mark.vcr
def test_should_hook_get_method(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("get")
        .using(transport)
        .dispatch(HttpMethod.get)
        .load(Echo)
        .assert_header(name="Handler", value="on_get")
    )


@pytest.mark.vcr
def test_should_hook_post_method(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("post")
        .using(transport)
        .dispatch(HttpMethod.post)
        .load(Echo)
        .assert_header(name="Handler", value="on_post")
    )


@pytest.mark.vcr
def test_should_hook_patch_method(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("patch")
        .using(transport)
        .dispatch(HttpMethod.patch)
        .load(Echo)
        .assert_header(name="Handler", value="on_patch")
    )


@pytest.mark.vcr
def test_should_hook_delete_method(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("delete")
        .using(transport)
        .dispatch(HttpMethod.delete)
        .load(Echo)
        .assert_header(name="Handler", value="on_delete")
    )


@pytest.fixture(params=["internal", "external"])
def transport(request: pytest.FixtureRequest) -> HttpTransport:
    if request.param == "internal":
        return Hooked(InternalEcho()).attach(_Hook())

    return Hooked(
        HttpxBuilder()
        .with_url(
            Environment().value_of(
                "ECHO_SERVER",
                default="http://localhost:8080",
            )
        )
        .transport()
    ).attach(_Hook())


@dataclass(frozen=True)
class _Hook(NoHook):
    name: str = "Handler"

    def before(
        self,
        using: HttpMethod,
        request: HttpRequest,
    ) -> HttpRequest:
        return request.with_header(key=self.name, value=f"on_{using.name}")
