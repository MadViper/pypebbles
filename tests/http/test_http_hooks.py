from dataclasses import dataclass

import pytest

from pypebbles.http import HttpMethod, HttpRequest, HttpResponse, HttpTransport
from pypebbles.http.domain.hooks import Hooked
from pypebbles.http.fake import InternalEcho
from pypebbles.http.httpx import HttpxBuilder
from pypebbles.runtime import Environment

from .echo import Echo


@pytest.mark.vcr
def test_should_trigger_on_get(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("get")
        .using(transport)
        .dispatch(HttpMethod.get)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "get", "X-AFTER": "get"})
    )


@pytest.mark.vcr
def test_should_trigger_on_post(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("post")
        .using(transport)
        .dispatch(HttpMethod.post)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "post", "X-AFTER": "post"})
    )


@pytest.mark.vcr
def test_should_trigger_on_patch(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("patch")
        .using(transport)
        .dispatch(HttpMethod.patch)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "patch", "X-AFTER": "patch"})
    )


@pytest.mark.vcr
def test_should_trigger_on_delete(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("delete")
        .using(transport)
        .dispatch(HttpMethod.delete)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "delete", "X-AFTER": "delete"})
    )


@pytest.fixture(params=["internal", "external"])
def transport(request: pytest.FixtureRequest) -> HttpTransport:
    return Hooked(_transport_of(kind=request.param)).attach(_Hook())


def _transport_of(kind: str) -> HttpTransport:
    match kind:
        case "external":
            return (
                HttpxBuilder()
                .with_url(
                    Environment().value_of(
                        "ECHO_SERVER",
                        default="http://localhost:8080",
                    )
                )
                .transport()
            )
        case "internal":
            return InternalEcho()
        case _:
            raise RuntimeError(f"Unknown kind: {kind}")


@dataclass(frozen=True)
class _Hook:
    def before(
        self,
        using: HttpMethod,
        request: HttpRequest,
    ) -> HttpRequest:
        return request.with_header(
            key="X-BEFORE",
            value=using.name,
        )

    def after(
        self,
        using: HttpMethod,
        request: HttpRequest,
        response: HttpResponse,
    ) -> HttpResponse:
        _ = request

        return response.set_json(
            {
                "json": {
                    "X-BEFORE": request.headers["X-BEFORE"],
                    "X-AFTER": using.name,
                }
            }
        )
