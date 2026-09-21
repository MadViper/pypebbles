from collections.abc import Mapping
from dataclasses import dataclass, field

import pytest
from faker import Faker


@dataclass(frozen=True)
class _Fake:
    faker: Faker = field(default_factory=Faker)

    def key(self) -> str:
        return self.faker.sentence(nb_words=32)

    def message(self) -> str:
        return self.faker.sentence()

    def payload(self) -> Mapping[str, str | int | float]:
        return self.faker.pydict(value_types=[str, int, float])


@pytest.fixture
def fake() -> _Fake:
    return _Fake()
