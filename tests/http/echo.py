from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Self

from pypebbles import JsonDict


@dataclass(frozen=True)
class Echo:
    raw: JsonDict

    def assert_header(self, name: str, value: str) -> Self:
        assert self.header(name=name) == value

        return self

    def header(self, name: str) -> str:
        return str(self.raw.value_of("headers").to(dict)[name])

    def assert_endpoint(self, *, expected: str) -> Self:
        assert self.endpoint() == expected

        return self

    def endpoint(self) -> str:
        return self.raw.value_of("url").to(str).rpartition("/")[-1]

    def assert_user_agent(self, *, expected: str) -> Self:
        assert self.header(name="User-Agent") == expected

        return self

    def assert_content_type(self, *, expected: str) -> Self:
        assert self.header(name="Content-Type") == expected

        return self

    def assert_json(self, *, expected: Mapping[str, Any]) -> Self:
        assert self._sub_object_of(key="json") == JsonDict(expected)

        return self

    def assert_form(self, *, expected: Mapping[str, Any]) -> Self:
        assert self._sub_object_of(key="form") == JsonDict(expected)

        return self

    def _sub_object_of(self, key: str) -> JsonDict:
        return JsonDict(self.raw.value_of(key).to(dict))
