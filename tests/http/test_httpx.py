import pytest

from pypebbles import JsonDict
from pypebbles.http import HttpMethod, HttpRequest, HttpTransport

from .echo import Echo


@pytest.mark.vcr
def test_should_post(echo: HttpTransport, a_json: JsonDict) -> None:
    (
        HttpRequest()
        .with_endpoint("post")
        .with_json(value=a_json)
        .using(echo)
        .dispatch(HttpMethod.post)
        .load(Echo)
        .assert_endpoint(expected="post")
        .assert_user_agent(expected="hogwarts")
        .assert_content_type(expected="application/json")
        .assert_json(expected=a_json)
    )


@pytest.mark.vcr
def test_should_submit(echo: HttpTransport, a_json: JsonDict) -> None:
    (
        HttpRequest()
        .with_endpoint("post")
        .with_data(value=a_json)
        .using(echo)
        .dispatch(HttpMethod.post)
        .load(Echo)
        .assert_endpoint(expected="post")
        .assert_user_agent(expected="hogwarts")
        .assert_content_type(expected="application/x-www-form-urlencoded")
        .assert_form(expected=a_json)
    )


@pytest.mark.vcr
def test_should_get(echo: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("get")
        .using(echo)
        .dispatch(HttpMethod.get)
        .load(Echo)
        .assert_endpoint(expected="get")
        .assert_user_agent(expected="hogwarts")
    )


@pytest.mark.vcr
def test_should_get_with_params(echo: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("get")
        .with_param("Color", "Yellow")
        .using(echo)
        .dispatch(HttpMethod.get)
        .load(Echo)
        .assert_endpoint(expected="get?Color=Yellow")
    )


@pytest.mark.vcr
def test_should_patch(echo: HttpTransport, a_json: JsonDict) -> None:
    (
        HttpRequest()
        .with_endpoint("patch")
        .with_json(value=a_json)
        .using(echo)
        .dispatch(HttpMethod.patch)
        .load(Echo)
        .assert_endpoint(expected="patch")
        .assert_user_agent(expected="hogwarts")
        .assert_content_type(expected="application/json")
        .assert_json(expected=a_json)
    )


@pytest.mark.vcr
def test_should_delete(echo: HttpTransport) -> None:
    (
        HttpRequest()
        .with_endpoint("delete")
        .using(echo)
        .dispatch(HttpMethod.delete)
        .load(Echo)
        .assert_endpoint(expected="delete")
        .assert_user_agent(expected="hogwarts")
    )


@pytest.mark.vcr
def test_should_put(echo: HttpTransport, a_json: JsonDict) -> None:
    (
        HttpRequest()
        .with_endpoint("put")
        .with_json(value=a_json)
        .using(echo)
        .dispatch(HttpMethod.put)
        .load(Echo)
        .assert_endpoint(expected="put")
        .assert_user_agent(expected="hogwarts")
        .assert_content_type(expected="application/json")
        .assert_json(expected=a_json)
    )


@pytest.fixture
def a_json() -> JsonDict:
    return JsonDict().with_a(Harry="Potter")
