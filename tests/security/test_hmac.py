from faker import Faker

from pypebbles.security import Hmac


def test_hmac_is_different_for_different_keys(faker: Faker) -> None:
    key_1 = faker.word()
    key_2 = faker.word()
    message = faker.sentence()

    assert Hmac(key_1)(message) != Hmac(key_2)(message)


def test_hmac_is_the_same_for_the_same_key(faker: Faker) -> None:
    key = faker.word()
    message = faker.sentence()

    assert Hmac(key)(message) == Hmac(key)(message)
