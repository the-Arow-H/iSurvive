"""Kit sales rule: price >= landed / 0.70 (gross margin at least 30%)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from isurvive.catalog import Catalog, Kit, load_catalog

MARGIN_DIVISOR = Decimal("0.70")


@dataclass(frozen=True)
class MarginCheck:
    sku: str
    landed_cents: int
    price_cents: int
    min_price_cents: int
    bom_sum_cents: int
    bom_matches_landed: bool
    ok: bool

    @property
    def gross_margin(self) -> float:
        if self.price_cents <= 0:
            return 0.0
        return (self.price_cents - self.landed_cents) / self.price_cents


def min_price_cents(landed_cents: int) -> int:
    if landed_cents < 0:
        raise ValueError("landed_cents must be >= 0")
    return int(
        (Decimal(landed_cents) / MARGIN_DIVISOR).to_integral_value(
            rounding=ROUND_CEILING
        )
    )


def evaluate_kit(kit: Kit) -> MarginCheck:
    floor = min_price_cents(kit.landed_cents)
    bom_sum = kit.bom_sum_cents()
    return MarginCheck(
        sku=kit.sku,
        landed_cents=kit.landed_cents,
        price_cents=kit.price_cents,
        min_price_cents=floor,
        bom_sum_cents=bom_sum,
        bom_matches_landed=bom_sum == kit.landed_cents,
        ok=kit.price_cents >= floor and bom_sum == kit.landed_cents,
    )


def evaluate_catalog(catalog: Catalog | None = None) -> list[MarginCheck]:
    cat = catalog or load_catalog()
    return [evaluate_kit(kit) for kit in cat.kits]


def failures(catalog: Catalog | None = None) -> list[MarginCheck]:
    return [row for row in evaluate_catalog(catalog) if not row.ok]
