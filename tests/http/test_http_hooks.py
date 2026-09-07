from dataclasses import dataclass

import pytest

from pypebbles.http import HttpMethod, HttpRequest, HttpResponse, HttpTransport
from pypebbles.http.domain.hooks import Hooked

from .echo import Echo


@pytest.mark.vcr
def test_should_trigger_on_get(hooked: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("get")
        .using(hooked)
        .dispatch(HttpMethod.get)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "get", "X-AFTER": "get"})
    )


@pytest.mark.vcr
def test_should_trigger_on_post(hooked: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("post")
        .using(hooked)
        .dispatch(HttpMethod.post)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "post", "X-AFTER": "post"})
    )


@pytest.mark.vcr
def test_should_trigger_on_patch(hooked: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("patch")
        .using(hooked)
        .dispatch(HttpMethod.patch)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "patch", "X-AFTER": "patch"})
    )


@pytest.mark.vcr
def test_should_trigger_on_delete(hooked: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("delete")
        .using(hooked)
        .dispatch(HttpMethod.delete)
        .load(Echo)
        .assert_json(expected={"X-BEFORE": "delete", "X-AFTER": "delete"})
    )


@pytest.fixture
def hooked(echo: HttpTransport) -> HttpTransport:
    return Hooked(echo).attach(_Hook())


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
