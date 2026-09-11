from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property


@dataclass(frozen=True)
class Amount:
    value: int = 0
    exponent: int = 1

    unit: str = "unknown"

    @classmethod
    def parse(cls, raw: str) -> Amount:
        value, exponent = Decimal(raw).as_integer_ratio()

        return cls(value=value, exponent=exponent)

    @cached_property
    def _gcd(self) -> int:
        return math.gcd(self.value, self.exponent)

    def reduce(self, when: bool = True) -> Amount:
        if not when:
            return self

        return Amount(
            value=self.value // self._gcd,
            exponent=self.exponent // self._gcd,
        )

    def invert(self) -> Amount:
        if self.value == 0:
            return self

        return Amount(value=self.exponent, exponent=self.value)

    def negate(self) -> Amount:
        return Amount(value=-self.value, exponent=self.exponent)

    def subtract(self, other: Amount) -> Amount:
        return self.add(other.negate())

    def add(self, other: Amount) -> Amount:
        if self.exponent == other.exponent:
            return Amount(
                value=self.value + other.value,
                exponent=self.exponent,
            )

        return Amount(
            value=self.value * other.exponent + other.value * self.exponent,
            exponent=self.exponent * other.exponent,
        ).reduce()

    def divide(self, other: Amount) -> Amount:
        return self.multiply(other.invert())

    def multiply(self, other: Amount) -> Amount:
        return Amount(
            value=self.value * other.value,
            exponent=self.exponent * other.exponent,
        ).reduce()

    def as_decimal(self) -> Decimal:
        return Decimal(self.value) / Decimal(self.exponent)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Amount):
            return self.as_decimal() == other.as_decimal()

        if isinstance(other, Decimal):
            return self.as_decimal() == other

        return False  # pragma: no cover

    def __float__(self) -> float:
        return float(self.as_decimal())
