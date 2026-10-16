import pytest
from faker import Faker

from pypebbles.http import HttpMethod, HttpRequest, PreSetHttp


def test_should_not_deliver_when_method_not_allowed(faker: Faker) -> None:
    # Given
    transport = PreSetHttp().allow(HttpMethod.get)
    request = HttpRequest(endpoint=faker.uri_path())

    # Then
    with pytest.raises(AssertionError, match="not allowed"):
        # When
        transport.deliver(request, using=HttpMethod.post)


def test_should_deliver_when_method_allowed(faker: Faker) -> None:
    # Given
    transport = PreSetHttp().allow(HttpMethod.get)
    request = HttpRequest(endpoint=faker.uri_path())

    # When
    response = transport.deliver(request, using=HttpMethod.get)

    # Then
    assert response.status == 200


def test_should_respond_with_pre_set_json(faker: Faker) -> None:
    # Given
    expected = faker.pydict(value_types=[str, int, float])
    transport = PreSetHttp().respond(expected).allow(HttpMethod.get)
    request = HttpRequest(endpoint=faker.uri_path())

    # When
    response = transport.deliver(request, using=HttpMethod.get)

    # Then
    assert response.json() == expected
