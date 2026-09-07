from dataclasses import dataclass

import pytest

from pypebbles import JsonDict
from pypebbles.http import HttpRequest, HttpTransport
from pypebbles.http.domain.hooks import Hooked
from pypebbles.http.drivers import Httpx
from pypebbles.http.security import SignPayloadWith
from pypebbles.security import Signature

from .echo import Echo


@dataclass(frozen=True)
class FakeAuthority:
    HEADER = "X-Header"

    def sign(self, message: str) -> Signature:
        return Signature(name=self.HEADER, value=message)

    def verify(self, message: str, signature: Signature) -> bool:
        raise NotImplementedError  # pragma: no cover


@pytest.fixture
def transport(echo_host: str) -> HttpTransport:
    return Hooked(Httpx.Builder().with_base(url=echo_host).build()).attach(
        SignPayloadWith(FakeAuthority())
    )


@pytest.mark.vcr
def test_should_hook_post_method(transport: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("post")
        .with_json(value=JsonDict().with_a(body="content"))
        .using(transport)
        .post()
        .load(Echo)
        .assert_header(name=FakeAuthority.HEADER, value='{"body":"content"}')
    )
