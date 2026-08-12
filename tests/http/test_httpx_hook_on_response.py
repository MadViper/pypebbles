from dataclasses import dataclass

import pytest

from pypebbles.http import HttpMethod, HttpRequest, HttpResponse, HttpTransport
from pypebbles.http.domain.hooks import Hooked, NoHook
from pypebbles.http.fake import InternalEcho
from pypebbles.http.httpx import HttpxBuilder
from pypebbles.runtime import Environment


@pytest.mark.vcr
def test_should_hook_get_method(transport: HttpTransport) -> None:
    with pytest.raises(ValueError, match="get"):
        HttpRequest().with_endpoint("get").using(transport).get()


@pytest.mark.vcr
def test_should_hook_post_method(transport: HttpTransport) -> None:
    with pytest.raises(ValueError, match="post"):
        HttpRequest().with_endpoint("post").using(transport).post()


@pytest.mark.vcr
def test_should_hook_patch_method(transport: HttpTransport) -> None:
    with pytest.raises(ValueError, match="patch"):
        HttpRequest().with_endpoint("patch").using(transport).patch()


@pytest.mark.vcr
def test_should_hook_delete_method(transport: HttpTransport) -> None:
    with pytest.raises(ValueError, match="delete"):
        HttpRequest().with_endpoint("delete").using(transport).delete()


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
    raises: type[Exception] = ValueError

    def after(
        self,
        using: HttpMethod,
        request: HttpRequest,
        response: HttpResponse,
    ) -> HttpResponse:
        _ = request, response

        raise self.raises(f"on_{using.name}")
