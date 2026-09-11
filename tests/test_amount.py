from dataclasses import replace

from hypothesis import given
from hypothesis.strategies import SearchStrategy, builds, integers

from pypebbles.amount import Amount


def _amounts(gt: int | None = None) -> SearchStrategy[Amount]:
    return builds(
        Amount,
        value=integers(min_value=gt + 1 if gt is not None else 0),
        exponent=integers(min_value=1, max_value=20).map(lambda x: 10**x),
    ).map(Amount.reduce)


@given(a=_amounts())
def test_self_equality(a: Amount) -> None:
    assert a == replace(a)


def test_static_factory() -> None:
    assert Amount.parse("1234567.89") == Amount(value=123456789, exponent=100)


@given(a=_amounts())
def test_addition_identity(a: Amount) -> None:
    assert a.add(Amount(0)) == a


@given(a=_amounts(), b=_amounts())
def test_addition_is_cumulative(a: Amount, b: Amount) -> None:
    assert a.add(b) == b.add(a)


@given(a=_amounts(), b=_amounts(), c=_amounts())
def test_addition_is_associative(a: Amount, b: Amount, c: Amount) -> None:
    assert (a.add(b)).add(c) == a.add(b.add(c))


@given(a=_amounts())
def test_multiplication_identity(a: Amount) -> None:
    assert a.multiply(Amount(1)) == a


@given(a=_amounts(), b=_amounts())
def test_multiplication_is_cumulative(a: Amount, b: Amount) -> None:
    assert a.multiply(b) == b.multiply(a)


@given(a=_amounts(), b=_amounts(), c=_amounts())
def test_multiplication_is_associative(a: Amount, b: Amount, c: Amount) -> None:
    assert (a.multiply(b)).multiply(c) == a.multiply(b.multiply(c))


@given(a=_amounts())
def test_subtraction_identity(a: Amount) -> None:
    assert a.subtract(Amount(0)) == a


@given(a=_amounts())
def test_should_get_zero_when_subtract_from_itself(a: Amount) -> None:
    assert a.subtract(a) == Amount(0)


@given(a=_amounts())
def test_division_identity(a: Amount) -> None:
    assert a.divide(Amount(1)) == a


@given(a=_amounts(gt=0))
def test_should_get_one_when_divided_by_itself(a: Amount) -> None:
    assert a.divide(a) == Amount(1)


@given(a=_amounts(), b=_amounts())
def test_addition_and_subtraction_are_inverses(a: Amount, b: Amount) -> None:
    assert a.add(b).subtract(b) == a
    assert a.add(b).subtract(a) == b


@given(a=_amounts(gt=0), b=_amounts(gt=0))
def test_multiplication_and_division_are_inverses(a: Amount, b: Amount) -> None:
    assert a.multiply(b).divide(b) == a
    assert a.multiply(b).divide(a) == b
