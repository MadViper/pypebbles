from collections.abc import Iterable
from dataclasses import dataclass, field, replace

import pytest
from faker.proxy import Faker
from pytest_apex import Ensure

from pypebbles.sync import Selector, SyncStage


@dataclass(frozen=True)
class Product:
    id: str
    barcode: str
    name: str


@dataclass(frozen=True)
class FakeProduct:
    fake: Faker = field(default_factory=Faker)

    def entity(self) -> Product:
        return Product(
            id=self.fake.uuid4(),
            barcode=self.fake.ean13(),
            name=self.fake.word(),
        )


@dataclass
class FakeTarget:
    items: list[Product] = field(default_factory=list)
    committed: list[Product] | None = None

    def __call__(self, items: Iterable[Product]) -> None:
        self.committed = list(items)


@dataclass(frozen=True)
class PreSelected(Selector[Product]):
    items: list[Product] = field(default_factory=list)
    requested: list[Product] = field(default_factory=list)

    def select(self, items: Iterable[Product]) -> Iterable[Product]:
        self.requested.extend(items)

        return self.items


@pytest.mark.parametrize("n_items", range(10))
def test_should_not_commit_when_dry(n_items: int) -> None:
    # Given
    target = FakeTarget(items=[FakeProduct().entity() for _ in range(n_items)])

    # When
    (
        SyncStage[Product]
        .using(target)
        .stage(target.items)
        .only_changes(when=False)
        .dry(when=True)
        .commit()
    )

    # Then
    assert target.committed is None


@pytest.mark.parametrize("n_items", range(2, 10))
def test_should_commit(ensure: Ensure, n_items: int) -> None:
    # Given
    target = FakeTarget(items=[FakeProduct().entity() for _ in range(n_items)])
    source = PreSelected(items=[FakeProduct().entity() for _ in range(n_items)])

    # When
    (
        SyncStage[Product]
        .using(target)
        .with_selector(source)
        .stage(target.items)
        .only_changes(when=False)
        .commit()
    )

    # Then
    ensure.iterables_equal(source.requested, expected=target.items)
    ensure.iterables_equal(target.committed, expected=source.items)


@pytest.mark.parametrize("n_items", range(2, 10))
def test_should_commit_only_changes(ensure: Ensure, n_items: int) -> None:
    # Given
    target = FakeTarget(items=[FakeProduct().entity() for _ in range(n_items)])
    source = PreSelected(
        items=[
            product
            if i % 2 == 0
            else replace(product, name=FakeProduct().entity().name)
            for i, product in enumerate(target.items)
        ]
    )

    # When
    (
        SyncStage[Product]
        .using(target)
        .with_selector(source)
        .stage(target.items)
        .only_changes(when=True)
        .commit()
    )

    # Then
    ensure.iterables_equal(source.requested, expected=target.items)
    ensure.iterables_equal(
        target.committed,
        expected=[product for i, product in enumerate(source.items) if i % 2 == 1],
    )
